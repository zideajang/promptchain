import asyncio

from rich.console import Console
from rich.panel import Panel

from promptchain.message import SystemMessage,Message,Messages
from promptchain.prompt import AIMessagePromptTemplate,HumanMessagePromptTemplate
from promptchain.chain_processor import ChainProcessor
from promptchain.processors import PrintMarkdownProcessor
from promptchain.llm import ChatMessageModel,OllamaChatMessageModel

console = Console()


async def simple_chain_example():
    # 初始化 messages
    system_message = SystemMessage(content="你是一个 linux 系统")
    assistant_message = AIMessagePromptTemplate.from_template("作为非常有帮助的助手")
    humam_message = HumanMessagePromptTemplate.from_template("ls")

    # 定义模型，现在只是支持 ollama 系列，随后我们会支持 deepseek 等更多供应商的模型
    model = OllamaChatMessageModel(name="test",model_name="qwen3:8b")
    
    # 初始化一个链式处理器
    chain = ChainProcessor(Messages(messages=[system_message]))

    print_markdown_tool = PrintMarkdownProcessor(name="print markdown",description="print markdown")
    
    # __or__ 方法，都是去显示或者隐式实现 Runnable 接口，需要实现 invoke 的函数
    # 随后提供 wrapper 通过 python 注释方法来对于普通函数也可以自由接入到 chain 
    chain | assistant_message | humam_message | model | print_markdown_tool

    # chain __or__ return chain __add__

    # 启动链，这样会进行一系列的动作
    await chain.invoke()
    
if __name__ == "__main__":
    asyncio.run(main=simple_chain_example())
