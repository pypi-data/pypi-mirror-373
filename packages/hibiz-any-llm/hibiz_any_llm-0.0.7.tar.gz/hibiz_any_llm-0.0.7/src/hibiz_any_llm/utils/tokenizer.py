import tiktoken
from typing import Optional, Dict
from abc import ABC, abstractmethod
from .constants import MODEL_ENCODINGS
from ..core.exceptions import TokenizationError

class BaseTokenizer(ABC):
    """Abstract base class for tokenizers"""
    
    @abstractmethod
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        pass

class TikTokenTokenizer(BaseTokenizer):
    """Tiktoken-based tokenizer for OpenAI models"""
    
    def __init__(self, default_encoding: str = "cl100k_base"):
        self.default_encoding = default_encoding
        self._encoders: Dict[str, tiktoken.Encoding] = {}
    
    def get_encoder(self, model_name: Optional[str] = None) -> tiktoken.Encoding:
        """Get appropriate encoder for model"""
        if not model_name:
            return tiktoken.get_encoding(self.default_encoding)
            
        if model_name not in self._encoders:
            try:
                # Check if we have a specific encoding for this model
                encoding_name = MODEL_ENCODINGS.get(model_name.lower())
                if encoding_name:
                    self._encoders[model_name] = tiktoken.get_encoding(encoding_name)
                else:
                    # Try to get model-specific encoding
                    self._encoders[model_name] = tiktoken.encoding_for_model(model_name)
            except Exception:
                # Fallback to default encoding
                self._encoders[model_name] = tiktoken.get_encoding(self.default_encoding)
        
        return self._encoders[model_name]
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        """Count tokens in text"""
        try:
            if not text:
                return 0
            encoder = self.get_encoder(model_name)
            return len(encoder.encode(text))
        except Exception as e:
            raise TokenizationError(f"Failed to count tokens: {e}")

class AnthropicTokenizer(BaseTokenizer):
    """Tokenizer for Anthropic models"""
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        return len(text.split()) * 1.3
class GeminiTokenizer(BaseTokenizer):
    """Tokenizer for Anthropic models"""
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        return len(text.split()) * 1.3
class QwenTokenizer(BaseTokenizer):
    """Tokenizer for Anthropic models"""
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        return len(text.split()) * 1.3
class GrokTokenizer(BaseTokenizer):
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        return len(text.split()) * 1.3
class DeepseekTokenizer(BaseTokenizer):
    """Tokenizer for Anthropic models"""
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        return len(text.split()) * 1.3

class TokenizerFactory:
    """Factory for creating appropriate tokenizers"""
    
    _tokenizers = {
        'tiktoken': TikTokenTokenizer,
        'anthropic': AnthropicTokenizer,
        'gemini': GeminiTokenizer,
        'qwen': QwenTokenizer,
        'grok': GrokTokenizer,
        'deepseek': DeepseekTokenizer
    }
    
    @classmethod
    def create_tokenizer(cls, tokenizer_type: str, **kwargs) -> BaseTokenizer:
        """Create a tokenizer of the specified type"""
        if tokenizer_type not in cls._tokenizers:
            raise TokenizationError(f"Unknown tokenizer type: {tokenizer_type}")
        
        return cls._tokenizers[tokenizer_type](**kwargs)