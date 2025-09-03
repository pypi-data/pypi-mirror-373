from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models.request import LLMRequest
from ..models.response import LLMResponse

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.lower().replace('provider', '')
    
    @abstractmethod
    def send_chat_completion(self, request: LLMRequest) -> LLMResponse:
        pass
    
    @abstractmethod
    def create_embeddings(self, request: LLMRequest) -> LLMResponse:
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        pass
    
    def get_provider_name(self) -> str:
        return self.provider_name