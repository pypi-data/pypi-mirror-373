from typing import Dict, Any, List
from ..utils.constants import LLMProvider
from ..providers.base import BaseLLMProvider
from ..providers.azure_openai import AzureOpenAIProvider
from ..providers.openai import OpenAIProvider
from ..providers.anthropic import AnthropicProvider
from ..providers.google import GoogleProvider
from ..providers.grok import GrokProvider
from ..providers.qwen import QwenProvider
from ..providers.deepseek import DeepSeekProvider
from ..providers.llama import LlamaProvider
from .exceptions import ConfigurationError

class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    _providers = {
        LLMProvider.AZURE_OPENAI: AzureOpenAIProvider,
        LLMProvider.OPENAI: OpenAIProvider,
        LLMProvider.ANTHROPIC: AnthropicProvider,
        LLMProvider.GOOGLE: GoogleProvider,
        LLMProvider.GROK: GrokProvider,
        LLMProvider.QWEN: QwenProvider,
        LLMProvider.DEEP_SEEK: DeepSeekProvider,
        LLMProvider.LLAMA: LlamaProvider
    }
    
    @classmethod
    def create_provider(cls, provider_type: LLMProvider, config: Dict[str, Any]) -> BaseLLMProvider:
        """Create a provider of the specified type"""
        if provider_type not in cls._providers:
            raise ConfigurationError(f"Unknown provider type: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def get_supported_providers(cls) -> List[LLMProvider]:
        """Get list of supported providers"""
        return list(cls._providers.keys())