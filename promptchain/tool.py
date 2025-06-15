import json
import inspect
from typing import Dict,Any,List
from promptchain.message import AIMessage,Messages,ToolMessage,ToolCallMessage
from rich.console import Console

console = Console()
class Tool:
    """
    A class to register functions and automatically generate their tool descriptions.
    """
    function_mapping = {}  # Stores the registered functions

    def __init__(self):
        self.tools = []  # Stores the generated tool descriptions

    def func(self, description: str = None):
        """
        A decorator to register a function and automatically generate its tool description.

        Args:
            description (str, optional): An optional description for the tool. If not provided,
                                         it will attempt to use the function's docstring.
        """
        def decorator(func):
            # Register the function in function_mapping
            self.function_mapping[func.__name__] = func

            # Automatically generate parameter description from function signature
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            sig = inspect.signature(func)
            for name, param in sig.parameters.items():
                json_schema_type = "string" # 默认值
                if param.annotation is not inspect.Parameter.empty:
                    # 将 Python 类型映射到 JSON Schema 类型
                    if param.annotation is str:
                        json_schema_type = "string"
                    elif param.annotation is int:
                        json_schema_type = "integer"
                    elif param.annotation is float:
                        json_schema_type = "number"
                    elif param.annotation is bool:
                        json_schema_type = "boolean"
                    # 这里可以根据需要添加更多复杂的类型映射，例如 list -> array, dict -> object
                    # 如果需要支持 Union 或 Optional 类型，还需要更复杂的解析逻辑
                    else:
                        # 对于复杂类型，可能需要更详细的错误处理或默认回退
                        print(f"Warning: Unhandled type annotation '{param.annotation}' for parameter '{name}'. Defaulting to 'string'.")
                        json_schema_type = "string" # 未识别的类型默认回退到 string

                parameters["properties"][name] = {
                    "type": json_schema_type,
                    "description": f"The {name} for the function." # Generic description, can be enhanced
                }
                # 假定所有没有默认值的参数都是必需的
                if param.default is inspect.Parameter.empty:
                    parameters["required"].append(name)

            # 获取函数描述，优先使用装饰器参数，然后是 docstring
            func_description = description if description else inspect.getdoc(func)
            if not func_description:
                func_description = f"A tool for calling the {func.__name__} function."

            # 构建工具描述
            tool_spec = {
                "type": "function",
                "function": {
                    "name": func.__name__,
                    "description": func_description.strip(), # Remove leading/trailing whitespace
                    "parameters": parameters,
                },
            }
            self.tools.append(tool_spec)

            return func
        return decorator
    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> ToolMessage:
        """
        Invokes the functions suggested by the language model and returns ToolMessage objects.

        Args:
            tool_call_message (ToolCallMessage): An object containing one or more tool calls
                                                 (e.g., from a model's response).

        Returns:
            List[ToolMessage]: A list of ToolMessage objects, each containing the output
                               of a tool call.
        """
        if not messages.messages:
            console.print(":x: 没有消息可供解析。")
            return
        last_message = messages.get_last_message()
        if not isinstance(last_message,ToolCallMessage):
            console.print("工具调用")
            return
        messages.pop_last_message()
        results = []
        console.print(last_message.tool_call)
        results: List[ToolMessage] = []
        tool_call = last_message.tool_call
        function_name = tool_call.function.name
        tool_call_id = tool_call.id
        arguments_str = tool_call.function.arguments

        if function_name not in self.function_mapping:
            error_content = f"Error: Function '{function_name}' not found in registered tools."
            results.append(ToolMessage(content=error_content, tool_call_id=tool_call_id))
            console.print(error_content)
            return
        
        target_function = self.function_mapping[function_name]

        try:
            # Parse the arguments string (which is JSON) into a Python dictionary
            # Use strict=False for older Python versions if needed, but strict=True is safer
            parsed_args = json.loads(arguments_str)

            # Call the function with the parsed arguments
            function_result = target_function(**parsed_args)
            results.append(ToolMessage(content=str(function_result), tool_call_id=tool_call_id))
        except json.JSONDecodeError:
            error_content = f"Error: Could not parse arguments for function '{function_name}': Invalid JSON '{arguments_str}'"
            results.append(ToolMessage(content=error_content, tool_call_id=tool_call_id))
        except TypeError as e:
            error_content = f"Error: Argument mismatch for function '{function_name}': {e}. Arguments received: {arguments_str}"
            results.append(ToolMessage(content=error_content, tool_call_id=tool_call_id))
        except Exception as e:
            error_content = f"Error executing function '{function_name}': {e}"
            results.append(ToolMessage(content=error_content, tool_call_id=tool_call_id))
        
        console.print(results[0])
        return results[0]