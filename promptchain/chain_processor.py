from abc import ABC,abstractmethod
from typing import Any,Protocol,List,Dict
from dataclasses import dataclass

from promptchain.message import Message,Messages

# 协议，在 python 协议是不需要显示实现
class Runnable(Protocol):
    async def invoke(self, messages: Messages, context: Dict[str, Any]) -> Messages|Message:
        ...

@dataclass
class ChainProcessor:
    chain_list:List[Runnable] 
    messages:Messages
    context: Dict[str, Any]

    def __init__(self,messages:Messages):
        self.chain_list =[]
        self.messages = messages
        self.context = {}

    def __or__(self, runnable: Runnable):
        self.chain_list.append(runnable)
        return self

    async def invoke(self,initial_context: Dict[str, Any] = None):
        if initial_context:
            self.context.update(initial_context)
            
        for runnable in self.chain_list:
            
            response_message = await runnable.invoke(self.messages, self.context)
            # TODO 并且是 message shape ("assistant","内容") {"role":"assistant","content":内容}
            # ["assistant","content"]
            if response_message is not None:
                self.messages.add_message(response_message)
        # TODO 
        return self.context


