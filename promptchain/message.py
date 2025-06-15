from typing import List, Literal, Union, Dict,Generator,Tuple,Any
from pydantic import BaseModel, Field,ValidationError
from rich.console import Console
import re
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall, Function

console = Console()


# 

class Message(BaseModel):
    role: Literal['system', 'assistant', 'user', 'tool']
    content: str

    # Ensure Message instances are hashable for set operations in Messages container
    class Config:
        frozen = True

    # --- TODO: 接收多种形式来构造的 Message ,{},(),[] ---
    # Using a custom validator for from_message to handle various inputs
    @classmethod
    def from_message(cls, message_input: Union[str, Dict, Tuple, List]) -> 'Message':
        """
        Constructs a Message instance from various input formats.

        Args:
            message_input (Union[str, Dict, Tuple, List]):
                - str: Will be treated as user content, role defaults to 'user'.
                - Dict: Expected to have 'role' and 'content' keys.
                - Tuple: Expected (role_str, content_str).
                - List: Expected [role_str, content_str].

        Returns:
            Message: A new Message instance.

        Raises:
            ValueError: If the input format is not recognized or invalid.
        """
        if isinstance(message_input, str):
            # Default to 'user' role for plain string input
            return cls(role='user', content=message_input)
        elif isinstance(message_input, Dict):
            try:
                # Direct parsing if it's a dict with role and content
                return cls(**message_input)
            except ValidationError as e:
                # If direct parsing fails, try inference
                if 'role' not in message_input or 'content' not in message_input:
                    # Attempt to infer role if keys are missing but content might be present
                    content_val = message_input.get('content') or message_input.get('text')
                    if content_val:
                        inferred_role = cls._infer_role_from_content(str(content_val))
                        return cls(role=inferred_role, content=str(content_val))
                raise ValueError(f"Invalid dictionary input for Message: {message_input}. Error: {e}")
        elif isinstance(message_input, (Tuple, List)):
            if len(message_input) == 2:
                role_str, content_str = message_input
                # Basic validation for role string
                if role_str not in ['system', 'assistant', 'user', 'tool']:
                    raise ValueError(f"Invalid role '{role_str}' in tuple/list input. Must be 'system', 'assistant', 'user', or 'tool'.")
                return cls(role=role_str, content=str(content_str))
            else:
                raise ValueError(f"Tuple or list input must have exactly two elements (role, content): {message_input}")
        else:
            raise TypeError(f"Unsupported message input type: {type(message_input)}. Expected str, Dict, Tuple, or List.")

    # Override the default __init__ to use from_message for flexible construction
    def __init__(self, **data):
        if 'role' not in data and 'content' not in data and len(data) == 1 and isinstance(list(data.values())[0], (str, Dict, Tuple, List)):
            # This handles cases like Message({'role': 'user', 'content': 'hi'})
            # or Message("hello"), Message(('user', 'hello')) directly as primary arg
            instance = self.from_message(list(data.values())[0])
            super().__init__(**instance.dict())
        elif 'role' in data and 'content' in data:
            super().__init__(**data)
        else:
            # Fallback for direct dict or other structured inputs if from_message doesn't catch
            # This allows Pydantic's default validation to kick in for standard dicts
            try:
                super().__init__(**data)
            except ValidationError:
                # If direct init fails, try to use from_message logic
                if 'content' in data:
                    # inferred_role = self._infer_role_from_content(data['content'])
                    inferred_role = "user"
                    super().__init__(role=inferred_role, content=data['content'])
                else:
                    raise ValueError(f"Could not construct Message from input: {data}. Missing 'role' or 'content' keys for direct init, and no suitable inference possible.")
    
    # def register_role_infer_strategy(self,strategy):
    #     self.strategy = strategy

    # # --- TODO: 推理类型也是 LLM-base 根据内容推理角色的 Message ---
    # @staticmethod
    # def _infer_role_from_content(content: str) -> Literal['system', 'assistant', 'user', 'tool']:
    #     """
    #     Infers the role based on common patterns in the message content.
    #     This is a heuristic and can be expanded or refined based on specific needs.
    #     """
    #     content_lower = content.lower().strip()
    #     if self.strategy:

    #     else:

    #         # Simple keyword-based inference
    #         # 添加策略
    #         if content_lower.startswith("as a language model") or \
    #         content_lower.startswith("i am an ai") or \
    #         content_lower.startswith("as an ai"):
    #             return 'assistant'
    #         if content_lower.startswith("tool call:") or \
    #         content_lower.startswith("calling tool:") or \
    #         re.match(r"^\w+\(.*\)$", content_lower): # Simple regex for function-like calls
    #             return 'tool'
    #         if content_lower.startswith("system:"):
    #             return 'system'
    #         if content_lower.startswith("user:"):
    #             return 'user'


class AIMessage(Message):
    role: str = "assistant"
    content: str

class HumanMessage(Message):
    role: str = "user"
    content: str

class SystemMessage(Message):
    role: str = "system"
    content: str

class ToolMessage(Message):
    role: str = "tool"
    content: str
    tool_call_id: str

class ToolCallMessage(Message):
    role:str = "tool"
    tool_call:Any

    def __repr__(self) -> str:
        """
        Returns a string representation of the object that can be used to recreate it.
        """
        tool_call_reprs = []
        if isinstance(self.tool_call, list):
            for tc in self.tool_call:
                if isinstance(tc, ChatCompletionMessageToolCall):
                    tool_call_reprs.append(
                        f"ChatCompletionMessageToolCall(id='{tc.id}', "
                        f"function=Function(arguments='{tc.function.arguments}', name='{tc.function.name}'), "
                        f"type='{tc.type}', index={tc.index})"
                    )
                else:
                    tool_call_reprs.append(repr(tc)) # Fallback for unexpected types
        else:
            tool_call_reprs.append(repr(self.tool_call)) # For single tool_call if it's not a list

        return (
            f"ToolCallMessage(role='{self.role}', tool_call=[{', '.join(tool_call_reprs)}])"
        )

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the object.
        """
        tool_call_strs = []
        if isinstance(self.tool_call, list):
            for tc in self.tool_call:
                if isinstance(tc, ChatCompletionMessageToolCall):
                    tool_call_strs.append(
                        f"  Tool Call ID: {tc.id}\n"
                        f"  Function Name: {tc.function.name}\n"
                        f"  Arguments: {tc.function.arguments}\n"
                        f"  Type: {tc.type}\n"
                        f"  Index: {tc.index}"
                    )
                else:
                    tool_call_strs.append(str(tc)) # Fallback
        else:
            tool_call_strs.append(str(self.tool_call)) # For single tool_call

        return (
            f"Role: {self.role}\n"
            f"Tool Calls:\n{'-' * 20}\n"
            f"{'\\n'.join(tool_call_strs)}"
        )

class Messages(BaseModel):
    messages: List[Message] = Field(default_factory=list) # Initialize with an empty list

    def _convert_to_message(self, item: Union[Message, Dict]|None) -> Message:
        if isinstance(item, Message):
            return item
        elif isinstance(item, Dict):
            try:
                return Message(**item)
            except Exception as e:
                raise ValueError(f"输入字典类数据无法转换为 Message: {item}. Error: {e}")
        else:
            raise TypeError(f"Unsupported message type: {type(item)}. Expected Message or Dict.")

    def add_message(self, message_input: Union[Message, Dict]):
        """Adds a single message to the list. Supports Message objects or dictionaries."""
        message = self._convert_to_message(message_input)
        self.messages.append(message)

    def __add__(self, other: Union[Message, Dict, List[Union[Message, Dict]]]):
        """
        Allows adding a single message or a list of messages.
        Supports Message objects, dictionaries, or lists thereof.
        Returns a new Messages object with the added messages.
        """
        new_messages_list = list(self.messages) # Create a copy to avoid modifying in place if chaining

        if isinstance(other, list):
            for item in other:
                new_messages_list.append(self._convert_to_message(item))
        else:
            new_messages_list.append(self._convert_to_message(other))

        return Messages(messages=new_messages_list)

    def __repr__(self):
        return f"Messages(count={len(self.messages)})"

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.messages)
    
    def __iter__(self) -> Generator[Message, None, None]:
        """
        Allows iteration over messages, acting as a generator.
        """
        yield from self.messages

    def __contains__(self, item: Union[Message, Dict]) -> bool:
        converted_item = self._convert_to_message(item)
        return converted_item in self.messages

    def __or__(self, other: "Messages") -> "Messages":
        """
        计算两个 messages 集合的并集
        返回一个新的 messages 包含 self 以及 other 中所有的 message
        """
        if not isinstance(other, Messages):
            raise TypeError(f"Unsupported operand type for |: 'Messages' and '{type(other).__name__}'")
        
        self_set = set(self.messages)
        other_set = set(other.messages)
        
        return Messages(messages=list(self_set.union(other_set)))

    def __sub__(self, other: "Messages") -> "Messages":
        """
        计算两个 message 的差集.
        """
        if not isinstance(other, Messages):
            raise TypeError(f"Unsupported operand type for -: 'Messages' and '{type(other).__name__}'")
        
        self_set = set(self.messages)
        other_set = set(other.messages)
        
        return Messages(messages=list(self_set.difference(other_set)))
    
    def query(self, role: str = None, content_contains: str = None) -> "Messages":
        """
        Queries messages based on specified criteria.
        
        Args:
            role (str, optional): Filters messages by role (e.g., 'user', 'assistant').
            content_contains (str, optional): Filters messages where content contains this substring.
            
        Returns:
            Messages: A new Messages object containing the filtered messages.
        """
        filtered_messages = []
        for msg in self.messages:
            match = True
            if role is not None and msg.role != role:
                match = False
            if content_contains is not None and content_contains not in msg.content:
                match = False
            
            if match:
                filtered_messages.append(msg)
        
        return Messages(messages=filtered_messages)
    
    def get_last_message(self) -> Union[Message, None]:
        """Returns the last message in the collection, or None if empty."""
        return self.messages[-1] if self.messages else None

    def get_first_message(self) -> Union[Message, None]:
        """Returns the first message in the collection, or None if empty."""
        return self.messages[0] if self.messages else None

    def to_list(self) -> List[Message]:
        """Returns the internal list of messages."""
        return list(self.messages)
    def pop_last_message(self) -> Union[Message, None]:
        """
        Removes and returns the last message in the collection, or None if empty.
        """
        if self.messages:
            return self.messages.pop()
        return None
