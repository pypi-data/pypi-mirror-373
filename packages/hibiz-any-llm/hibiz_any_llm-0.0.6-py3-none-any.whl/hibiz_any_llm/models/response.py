from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Union

@dataclass
class TokenUsage:
    """Token usage information"""
    input_tokens: int
    output_tokens: int
    total_tokens: int

@dataclass
class LLMResponse:
    """Standardized response model for all LLM providers"""
    success: bool
    output_text: Optional[str] = None
    processed_output: Optional[Any] = None
    embeddings: Optional[Union[List[float], List[List[float]]]] = None
    token_usage: Optional[TokenUsage] = None
    response_time_ms: int = 0
    model: Optional[str] = None
    provider: Optional[str] = None
    request_id: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)