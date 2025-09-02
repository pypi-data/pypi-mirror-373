from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from enum import Enum

class ResponseType(Enum):
    TEXT = "text"
    JSON = "json"

class RequestType(Enum):
    CHAT_COMPLETION = "chat_completion"
    EMBEDDING = "embedding"
    COMPLETION = "completion"

@dataclass
class LLMRequest:
    """Standardized request model for all LLM providers"""
    customer_id: str
    organization_id: str
    app_name: str
    module_name: str
    function_name: str
    request_type: RequestType
    model: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    prompt: Optional[str] = None
    input_texts: Optional[Union[str, List[str]]] = None
    response_type: ResponseType = ResponseType.TEXT
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)