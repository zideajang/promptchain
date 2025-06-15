import asyncio
import json
from typing import TypeVar, Type, Dict, Any, Generic
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, ValidationError
from promptchain.message import AIMessage
from rich.console import Console
from rich.panel import Panel

console = Console()

# 如果实际文件路径不同，请根据您的 PromptChain 版本调整
from promptchain.message import Messages, Message

T = TypeVar("T", bound=BaseModel)

# --- 1. 定义抽象的 Parser 类 ---
class Parser(ABC):
    """
    一个抽象的解析器类，用于处理消息并可能更新上下文。
    """
    @abstractmethod
    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> None:
        """
        抽象方法，用于解析消息并更新上下文。
        解析器不应向消息历史中添加新消息。
        """
        pass

# --- 2. 实现 PydanticParser，继承 Parser 抽象类 ---
class PydanticParser( Parser, Generic[T]): # 继承 Tool 和 Parser
    def __init__(self, pydantic_model: Type[T], output_key: str = "parsed_output"):
        # PydanticParser 也可能作为一个 Tool 使用，所以我们保留 Tool 的初始化
        self.pydantic_model = pydantic_model
        self.output_key = output_key

    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> None:
        """
        实现 Parser 抽象类的 invoke 方法。
        解析 LLM 的输出并将其存储在上下文中。
        """
        if not messages.messages:
            console.print(":x: 没有消息可供解析。")
            return

        last_message = messages.get_last_message()
        content = last_message.content

        try:
            # 尝试从内容中提取 JSON 字符串
            # 这是一个简单的提取逻辑，可能需要根据 LLM 输出的实际情况进行调整
            start_index = content.find('{')
            end_index = content.rfind('}') + 1

            if start_index == -1 or end_index == -1 or start_index >= end_index:
                raise ValueError("未在消息内容中找到有效的 JSON 结构。")

            json_str = content[start_index:end_index]
            json_obj = json.loads(json_str)

            # 使用 Pydantic 模型解析 JSON 对象
            parsed_obj = self.pydantic_model.model_validate(json_obj) # 推荐使用 model_validate
            context[self.output_key] = parsed_obj
            console.print(f":white_check_mark: 输出已解析并存储在 context['{self.output_key}'] 中。")
        except (json.JSONDecodeError, ValidationError, ValueError, IndexError) as e:
            console.print(f":x: 解析输出失败: {e}")
            context[f"{self.output_key}_error"] = str(e)
            # 可以选择在这里将原始内容或错误信息添加到上下文，以便调试
            context[f"{self.output_key}_raw_content"] = content
        
        # 按照 Parser 抽象方法的约定，不返回任何值 (返回 None)
        return  AIMessage(content=json_obj)