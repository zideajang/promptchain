import asyncio

from rich.console import Console
from rich.panel import Panel

from promptchain.message import SystemMessage,Message,Messages
from promptchain.prompt import AIMessagePromptTemplate,HumanMessagePromptTemplate
from promptchain.chain_processor import ChainProcessor
from promptchain.processors import PrintMarkdownProcessor
from promptchain.llm import DeepseekChatMessageModel
from promptchain.tool import Tool
console = Console()

tool_manager = Tool()

@tool_manager.func()
def get_weather(city_name:str)->str:
    """
    返回指定城市的温度
    """
    return 27.5

# 在这里查看类及其自动提取函数生成工具 Schema 
# console.print(tool_manager.tools)
# exit(0)


async def simple_chain_function_calling_example():
    # 初始化 messages
    system_message = SystemMessage(content="作为非常有帮助的助手")
    humam_message = HumanMessagePromptTemplate.from_template("沈阳今天的气温是多少")

    # 定义模型，现在只是支持 ollama 系列，随后我们会支持 deepseek 等更多供应商的模型
    
    model = DeepseekChatMessageModel(name="test",model_config={
        "tools":tool_manager.tools
    })
    
    # 初始化一个链式处理器
    chain = ChainProcessor(Messages(messages=[system_message]))
    
    chain |  humam_message | model | tool_manager 

    await chain.invoke()
    
if __name__ == "__main__":
    asyncio.run(main=simple_chain_function_calling_example())
