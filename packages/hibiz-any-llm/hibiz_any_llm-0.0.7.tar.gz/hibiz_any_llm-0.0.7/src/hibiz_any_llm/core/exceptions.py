class LLMWrapperError(Exception):
    """Base exception for LLM Wrapper"""
    pass

class DatabaseError(LLMWrapperError):
    """Database-related errors"""
    pass

class APIError(LLMWrapperError):
    """API-related errors"""
    pass

class TokenizationError(LLMWrapperError):
    """Tokenization-related errors"""
    pass

class ProviderError(LLMWrapperError):
    """Provider-related errors"""
    pass

class ConfigurationError(LLMWrapperError):
    """Configuration-related errors"""
    pass

class ValidationError(LLMWrapperError):
    """Validation-related errors"""
    pass