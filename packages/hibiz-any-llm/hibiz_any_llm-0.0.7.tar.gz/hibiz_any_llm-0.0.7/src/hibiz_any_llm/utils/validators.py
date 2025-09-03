from typing import Dict, Any
from ..core.exceptions import ValidationError
from ..models.request import LLMRequest

class ParameterValidator:

    PARAMETER_RANGES = {
        'openai': {
            "temperature": (0.0, 2.0),
            "top_p": (0.0, 1.0),
            "frequency_penalty": (-2.0, 2.0),
            "presence_penalty": (-2.0, 2.0),
            "max_tokens": (1, 128000)
        },
        'anthropic': {
            "temperature": (0.0, 1.0),
            "top_p": (0.0, 1.0),
            "max_tokens": (1, 20000)
        },
        'gemini': {
            "temperature": (0.0, 1.0),
            "top_p": (0.0, 1.0),
            "max_tokens": (1, 20000)
        },
        'grok': {
            "temperature": (0.0, 1.0),
            "top_p": (0.0, 1.0),
            "max_tokens": (1, 20000)
        },
        'qwen': {
            "temperature": (0.0, 1.0),
            "top_p": (0.0, 1.0),
            "max_tokens": (1, 20000)
        },
        'deepseek': {
            "temperature": (0.0, 1.0),
            "top_p": (0.0, 1.0),
            "max_tokens": (1, 20000)
        },
        'llama': {
            "temperature": (0.0, 1.0),
            "top_p": (0.0, 1.0),
            "max_tokens": (1, 20000)
        }
    }
    
    @classmethod
    def validate_parameters(cls, params: Dict[str, Any], provider: str = 'openai') -> Dict[str, Any]:
        """Validate and sanitize parameters"""
        validated = {}
        ranges = cls.PARAMETER_RANGES.get(provider, cls.PARAMETER_RANGES['openai'])
        
        for key, value in params.items():
            if key in ranges:
                min_val, max_val = ranges[key]
                if isinstance(value, (int, float)):
                    validated[key] = max(min_val, min(max_val, value))
                else:
                    validated[key] = value
            else:
                validated[key] = value
        
        return validated
    
    @classmethod
    def validate_request(cls, request: 'LLMRequest') -> None:
        """Validate LLM request"""
        if not request.customer_id:
            raise ValidationError("customer_id is required")
        if not request.organization_id:
            raise ValidationError("organization_id is required")
        if not request.app_name:
            raise ValidationError("app_name is required")