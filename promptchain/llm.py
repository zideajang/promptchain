from abc import ABC,abstractmethod
from typing import Any,Dict
from uuid import uuid4

import ollama
from openai import AsyncOpenAI,OpenAI

from rich.console import Console


from promptchain.message import Messages,AIMessage,ToolCallMessage
from promptchain.constants import DEEPSEEK_API_KEY,DEEPSEEK_BASE_URL

console = Console()

def build_model(model):
    def invoke(prompt):
        response = ollama.chat(
            model=model,
            messages=[{
                "role":"user",
                "content":prompt
            }]
        )
        return response['message']['content']
    return invoke


def build_embedding_model(model_name:str):
    def invoke(prompt_str:str):
        response = ollama.embeddings(model=model_name, prompt=prompt_str)
        return response["embedding"]
    
    return invoke

def build_chat_message_model(model_name:str):
    def intial_system(system_content:str):
        def intial_assistent(asistent_content:str):
            def invoke(prompt_str:str):
                response =  ollama.chat(
                    model=model_name,
                    messages=[
                        {
                            "role":"system",
                            "content":system_content
                        },
                         {
                            "role":"assistant",
                            "content":asistent_content
                        },
                        {
                            "role":"user",
                            "content":prompt_str
                        }]
                )
                return response['message']['content']
            return invoke
        return intial_assistent
    return intial_system

def build_chat_model(model_name:str):
    def intial_system(system_content:str):
        async def invoke(prompt_str:str):
            response =  ollama.chat(
                model=model_name,
                messages=[
                    {
                        "role":"system",
                        "content":system_content
                    },
                    {
                        "role":"user",
                        "content":prompt_str
                    }]
            )
            return response['message']['content']
        return invoke
    return intial_system

# TODO 更新到 ollama 最新版本，支持 think 开启和关闭

class ChatMessageModel(ABC):
    def __init__(self,
            name:str,     
            model_name:str,
            client:str|Any,
            model_config:Dict[str,Any]|None = None
            ) -> None:
        self.name = name
        self.model_id = uuid4()
        self.client = client if client else None
        
        self.model_name = model_name
        self.model_config = model_config if model_config else {}
    @abstractmethod
    async def invoke(self,messages:Messages, context: Dict[str, Any]):
        pass

class DeepseekChatMessageModel(ChatMessageModel):
    def __init__(self, name, model_name:str = "deepseek-chat", model_config:Dict[str,Any]|None = None):
        client = OpenAI(api_key=DEEPSEEK_API_KEY,base_url=DEEPSEEK_BASE_URL)
        super().__init__(name, model_name,client, model_config)

    async def invoke(self,messages:Messages, context: Dict[str, Any] = None):

        updated_messages  = []
        for message in messages.messages:
            if message.role in ['user','assistant','system']:
                updated_messages.append(message.model_dump())
            else:
                updated_messages.append({
                    "role":message.role,
                    "content":message.content,
                    "tool_call_id":message.tool_call_id
                })


        # 更新 model config 的配置
        console.print(messages)
        if self.model_config:
            self.model_config['messages'] = updated_messages
            self.model_config['model'] = self.model_name
        else:
            self.model_config = {
                "model":self.model_name,
                "messages":updated_messages,
            }

        console.print(self.model_config)
        response = self.client.chat.completions.create(**self.model_config)
        if response.choices[0].message.content:
            ai_message = AIMessage(content=response.choices[0].message.content)
            return ai_message
        elif response.choices[0].message.tool_calls:
            tool_message = ToolCallMessage(
                content=response.choices[0].message.content,
                tool_call=response.choices[0].message.tool_calls[0])
            return tool_message
        
class OllamaChatMessageModel(ChatMessageModel):
    # Ollama model_config 
    def __init__(self, name, model_name,  model_config = None):
        super().__init__(name, model_name, "ollama", model_config)

    async def invoke(self,messages:Messages, context: Dict[str, Any] = None):
        # TODO context 提取到模型相关配置
        # TODO 对于模型配置进行抽象

        # 更新 model config 的配置
        if self.model_config:
            self.model_config['messages'] = messages.model_dump()['messages']
            self.model_config['model'] = self.model_name
        else:
            self.model_config = {
                "model":self.model_name,
                "messages":messages.model_dump()['messages'],

            }
        # 在这里打印 self.model_config
        response = ollama.chat(**self.model_config)

        
        # 如果 content=response['message']['content'] 为空，而
        

        ai_message = AIMessage(content=response['message']['content'])
        
        if context is not None:
            context['llm_output'] = ai_message
            
        return ai_message



