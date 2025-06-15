import asyncio

from rich.console import Console
from rich.panel import Panel

from promptchain.message import SystemMessage,Message,Messages
from promptchain.prompt import AIMessagePromptTemplate,HumanMessagePromptTemplate
from promptchain.chain_processor import ChainProcessor
from promptchain.tool import PrintMarkdownTool,ExtractCodeTool
from promptchain.llm import ChatMessageModel


async def simple_code_example():
    system_message = SystemMessage(content="you are python expert")

    assistant_message = AIMessagePromptTemplate.from_template("you are very help assistant")
    humam_message = HumanMessagePromptTemplate.from_template("write read file programming in python")

    model = ChatMessageModel("qwen3:8b")
    
    chain = ChainProcessor(Messages(messages=[system_message]))

    print_markdown_tool = PrintMarkdownTool(name="print markdown",description="print markdown")
    extract_code_tool = ExtractCodeTool(name="extract code",description="extract code from response")

    chain | assistant_message | humam_message | model | print_markdown_tool| extract_code_tool
    await chain.invoke()

if __name__ == "__main__":
    asyncio.run(main=simple_code_example())