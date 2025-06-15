from typing import Dict,Optional,List,Any
import re
from pydantic import BaseModel, Field
from promptchain.message import Message,AIMessage,HumanMessage,SystemMessage,Messages

class MessagePromptTemplate(BaseModel):
    template:str
    input_variables: List[str] = Field(default_factory=list)
    @classmethod
    def from_template(cls,template:str):
        variables = re.findall(r"\{(\w+)\}", template)
        return cls(template=template, input_variables=variables)
    
    def format(self,**kwargs):
        return self.template.format(**kwargs)
    
    # TODO 如何将 messages 容器到(Messages)作为示例，
    async def invoke(self, messages: Messages|None, context: Dict[str, Any]) -> Message:
        format_args = {key: context[key] for key in self.input_variables}
        content = self.format(**format_args)

        # TODO 当 message 不为空时候，
        
        if isinstance(self, SystemMessagePromptTemplate):
            return SystemMessage(content=content)
        if isinstance(self, AIMessagePromptTemplate):
            return AIMessage(content=content)
        if isinstance(self, HumanMessagePromptTemplate):
            return HumanMessage(content=content)
        raise TypeError("没有匹配类型")

class SystemMessagePromptTemplate(MessagePromptTemplate):
    pass

class AIMessagePromptTemplate(MessagePromptTemplate):
    pass
    
class HumanMessagePromptTemplate(MessagePromptTemplate):
    pass


