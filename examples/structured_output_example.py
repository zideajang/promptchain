import asyncio
from pydantic import BaseModel, Field
from typing import List, Any
import json

from promptchain.chain_processor import ChainProcessor
from promptchain.llm import DeepseekChatMessageModel
from promptchain.message import Messages, SystemMessage
from promptchain.prompt.prompt import HumanMessagePromptTemplate,SystemMessagePromptTemplate
from promptchain.parser import PydanticParser
from promptchain.utils import create_example_from_model

from rich.console import Console

console = Console()

# 辅助函数：根据 Pydantic 模型及其示例生成 JSON 示例


# 1. 定义所需的数据结构 (Pydantic 模型)
class Tut(BaseModel):
    title: str = Field(description="文章的标题", examples=["Python 函数式编程指南"])
    topic: str = Field(description="文章的主要主题", examples=["Python 中的函数式编程"])
    chapter: List[str] = Field(description="文章章节的大纲", examples=[["引言", "高阶函数", "不可变性", "纯函数", "闭包与装饰器", "总结"]])
    
# 2. 为此结构创建解析工具
# 注意：PromptChain 的 PydanticParserTool 才是正确的类名
parser = PydanticParser(pydantic_model=Tut, output_key="tut")

# 3. 创建一个请求 JSON 格式数据的提示
system_prompt = SystemMessagePromptTemplate.from_template(
    """
EXAMPLE INPUT:
**文章主题为**： {topic}

EXAMPLE JSON OUTPUT:
{example}

"""
)

human_prompt = HumanMessagePromptTemplate.from_template("**文章主题为**：\n python 中的 generator")

system_message = system_prompt.format(topic="Python 中的异步编程",example=create_example_from_model(Tut))


# 4. 配置链
async def main():
    model = DeepseekChatMessageModel("parser_demo")
    
    chain = ChainProcessor(Messages(messages=[
        SystemMessage(content=system_message)
    ]))
    
    # 5. 定义链的流程，将解析器放在模型之后
    chain  | human_prompt| model | parser
    context = await chain.invoke()
    console.print(context)
    

if __name__ == "__main__":
    asyncio.run(main())