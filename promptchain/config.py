from typing import Optional
from dataclasses import dataclass


@dataclass
class BaseModelConfig:
    model_name:str
    model_endpoint:Optional[str] = None 

@dataclass
class LLMConfig(BaseModelConfig):
    context_window:Optional[int] = None

@dataclass
class EmbeddingConfig(BaseModelConfig):

    embedding_dim:Optional[int] = 512
    embedding_chuck_size:Optional[int] = 300
    

@dataclass
class PromptChainConfig:
    archival_storage_type = "json"
    archival_storage_path = "db"