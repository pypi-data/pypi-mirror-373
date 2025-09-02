from enum import Enum

class LLMProvider(Enum):
    AZURE_OPENAI = "azure_openai"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROK = "grok"
    QWEN = "qwen"
    DEEP_SEEK = "deepseek"
    LLAMA = "llama"

# Model to encoding mapping for tiktoken
MODEL_ENCODINGS = {
    # OpenAI models
    "gpt-4": "cl100k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-4o": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "text-embedding-ada-002": "cl100k_base",
    "text-embedding-3-small": "cl100k_base",
    "text-embedding-3-large": "cl100k_base",
    
    # Add more model mappings as needed
}

DEFAULT_TIMEOUTS = {
    LLMProvider.AZURE_OPENAI: 600,
    LLMProvider.OPENAI: 600,
    LLMProvider.ANTHROPIC: 300,
    LLMProvider.GOOGLE: 300,
    LLMProvider.GROK: 300,
    LLMProvider.QWEN: 300,
    LLMProvider.DEEP_SEEK: 300,
    LLMProvider.LLAMA: 600,
}