from abc import ABC,abstractmethod
from typing import Dict,Any,Union,Optional,List

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown


from promptchain.message import Message,Messages,ToolMessage
from promptchain.code_utils import extract_code

console = Console()

class Processor(ABC):
    name: str = "AbstractProcessor" 
    @abstractmethod
    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> Optional[Union[Message, List[Message]]]:
        pass

class PrintMarkdownProcessor(Processor):
    name: str = "PrintMarkdownProcessor"

    def __init__(self,description:str):
        super().__init__()
        self.description = description

    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> None: # Returns None
        """
        Prints the content of the last message formatted as Markdown.
        """
        message = messages.get_last_message() # Use the property for cleaner access
        if not message:
            print(f"[{self.name}] No message to print.")
            return None

        if console:
            console.print(
                Panel(Markdown(message.content), title=self.description, expand=True) # Use expand=True for better rendering
            )
        else:
            print(f"[{self.description}] Markdown Output:\n{message.content}")

        return None # This processor's primary effect is a side-effect (printing)

class PrintJsonProcessor(Processor):
    name: str = "PrintJsonProcessor"

    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> None: # Returns None
        """
        Prints the last message as a JSON representation.
        """
        message = messages.get_last_message()
        if not message:
            print(f"[{self.name}] No message to print.")
            return None

        if console:
            # Pydantic v2 uses model_dump_json(), v1 uses json()
            json_output = message.model_dump_json() if hasattr(message, 'model_dump_json') else message.json()
            console.print_json(json_output)
        else:
            # Fallback for basic print if rich is not available
            print(f"[{self.name}] JSON Output:\n{message.model_dump_json() if hasattr(message, 'model_dump_json') else message.json()}")
        return None

class ExtractCodeProcessor(Processor):
    name: str = "ExtractCodeProcessor"

    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> List[ToolMessage]:
        """
        Extracts code blocks from the content of the last message.
        Returns a list of ToolMessage objects, each containing an extracted code block.
        """
        message = messages.last_message
        if not message:
            print(f"[{self.name}] No message to extract code from.")
            return []

        extracted_tools = []
        # extract_code is expected to return a list of (language, code) tuples
        for lang, code_content in extract_code(message.content):
            # You might want to include 'lang' in content or as a separate field in ToolMessage
            extracted_tools.append(ToolMessage(
                role="tool", # Assuming extracted code is meant for tool execution
                content=code_content,
                tool_name=lang # Storing language as tool_name for context
            ))
        
        if not extracted_tools:
            print(f"[{self.name}] No code blocks found in the message.")

        return extracted_tools
class ExtractCodeProcessor(Processor):
    async def invoke(self, messages: Messages,context: Dict[str, Any]) -> Message:
        message = messages.get_last_message()
        result = []
        if isinstance(message,Message):
            for tool in extract_code(message.content):
                result.append(ToolMessage(
                    content=tool[1]
                ))
        return result