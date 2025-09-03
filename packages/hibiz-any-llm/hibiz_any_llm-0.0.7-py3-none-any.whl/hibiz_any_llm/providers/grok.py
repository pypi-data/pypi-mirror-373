import requests
import time
import json
import uuid
from typing import Dict, Any, List
from .base import BaseLLMProvider
from ..models.request import LLMRequest, ResponseType
from ..models.response import LLMResponse, TokenUsage
from ..utils.tokenizer import TokenizerFactory
from ..utils.validators import ParameterValidator
from ..core.exceptions import APIError, ConfigurationError

class GrokProvider(BaseLLMProvider):
    """xAI Grok provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config['api_key']
        self.base_url = config.get('base_url', 'https://api.x.ai')
        self.timeout = config.get('timeout', 300)
        self.default_model = config.get('default_model', 'grok-beta')
        
        # Initialize tokenizer
        self.tokenizer = TokenizerFactory.create_tokenizer('grok')
        
        self.validate_config()
    
    def validate_config(self) -> bool:
        """Validate Grok configuration"""
        if not self.config.get('api_key'):
            raise ConfigurationError("Missing required field: api_key")
        return True
    
    def send_chat_completion(self, request: LLMRequest) -> LLMResponse:
        """Send chat completion request to Grok"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Convert messages to Grok format (OpenAI-compatible)
            grok_messages = self._convert_messages(request.messages)
            
            # Validate and prepare parameters
            validated_params = ParameterValidator.validate_parameters(
                request.parameters, 'grok'
            )
            
            # Prepare request payload for Grok
            request_params = {
                "model": request.model or self.default_model,
                "messages": grok_messages,
                "max_tokens": validated_params.get("max_tokens", 4000),
                "temperature": validated_params.get("temperature", 0.7),
                "top_p": validated_params.get("top_p", 0.9),
                "frequency_penalty": validated_params.get("frequency_penalty", 0.0),
                "presence_penalty": validated_params.get("presence_penalty", 0.0),
                "stop": validated_params.get("stop", None),
                "stream": False
            }
            
            # Remove None values
            request_params = {k: v for k, v in request_params.items() if v is not None}
            
            # Make API request
            response_data = self._make_chat_api_request(request_params)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Process response
            return self._process_chat_response(response_data, request, response_time_ms, request_id)
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return LLMResponse(
                success=False,
                error_message=str(e),
                response_time_ms=response_time_ms,
                model=request.model or self.default_model,
                provider=self.provider_name,
                request_id=request_id
            )
    
    def create_embeddings(self, request: LLMRequest) -> LLMResponse:
        """Grok doesn't provide embeddings, raise error"""
        return LLMResponse(
            success=False,
            error_message="Grok does not provide embedding services",
            provider=self.provider_name
        )
    
    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI-style messages to Grok format (OpenAI-compatible)"""
        grok_messages = []
        
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            
            # Grok uses OpenAI-compatible format
            if role in ["system", "user", "assistant"]:
                grok_messages.append({
                    "role": role,
                    "content": content if isinstance(content, str) else str(content)
                })
        
        return grok_messages
    
    def _make_chat_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make chat completion API request to Grok"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/v1/chat/completions"
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_api_error(response)
                
        except requests.RequestException as e:
            raise APIError(f"HTTP request failed: {e}")
    
    def _handle_api_error(self, response):
        """Handle API error responses"""
        try:
            error_data = response.json()
            error_detail = error_data.get("error", {}).get("message", response.text)
        except ValueError:
            error_detail = response.text
        
        raise APIError(f"Grok API request failed with status {response.status_code}: {error_detail}")
    
    def _process_chat_response(
        self,
        response_data: Dict[str, Any],
        request: LLMRequest,
        response_time_ms: int,
        request_id: str
    ) -> LLMResponse:
        output_text = ""
        
        if "choices" in response_data and response_data["choices"]:
            choice = response_data["choices"][0]
            if "message" in choice and "content" in choice["message"]:
                output_text = choice["message"]["content"]
        
        # Process output based on response type
        processed_output = self._process_output_by_type(
            output_text, request.response_type
        )
        
        # Extract token usage from response
        usage = response_data.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", input_tokens + output_tokens)
        
        # Fallback to tokenizer if usage not provided
        if not usage:
            input_text = self._extract_text_from_messages(request.messages)
            input_tokens = self.tokenizer.count_tokens(input_text)
            output_tokens = self.tokenizer.count_tokens(output_text)
            total_tokens = input_tokens + output_tokens
        
        return LLMResponse(
            success=True,
            output_text=output_text,
            processed_output=processed_output,
            token_usage=TokenUsage(input_tokens, output_tokens, total_tokens),
            response_time_ms=response_time_ms,
            model=request.model or self.default_model,
            provider=self.provider_name,
            request_id=request_id,
            raw_response=response_data
        )
    
    def _extract_text_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Extract text content from messages for token calculation"""
        text_parts = []
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            text_parts.append(f"{role}: {content}")
        
        return "\n".join(text_parts)
    
    def _process_output_by_type(self, output_text: str, response_type: ResponseType) -> Any:
        """Process output based on the specified response type"""
        if response_type == ResponseType.JSON:
            try:
                return json.loads(output_text)
            except json.JSONDecodeError as e:
                return {
                    "error": f"Failed to parse JSON: {str(e)}",
                    "raw_output": output_text
                }
        else:
            return output_text