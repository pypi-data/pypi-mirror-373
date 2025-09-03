import requests
import time
import json
import uuid
import re
from typing import Dict, Any, List
from .base import BaseLLMProvider
from ..models.request import LLMRequest, ResponseType
from ..models.response import LLMResponse, TokenUsage
from ..utils.validators import ParameterValidator
from ..core.exceptions import APIError, ConfigurationError

class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config['api_key']
        self.base_url = config.get('base_url', 'https://generativelanguage.googleapis.com')
        self.timeout = config.get('timeout', 300)
        self.default_model = config.get('default_model', 'gemini-2.5-pro')
 
        self.validate_config()
    
    def validate_config(self) -> bool:
        """Validate Google Gemini configuration"""
        if not self.config.get('api_key'):
            raise ConfigurationError("Missing required field: api_key")
        return True
    
    def send_chat_completion(self, request: LLMRequest) -> LLMResponse:
        """Send chat completion request to Google Gemini"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Convert OpenAI-style messages to Gemini format
            gemini_contents = self._convert_messages(request.messages)
            
            # Validate and prepare parameters
            validated_params = ParameterValidator.validate_parameters(
                request.parameters, 'google'
            )
            
            # Prepare request payload for Gemini
            request_params = {
                "contents": gemini_contents,
                "generationConfig": {
                    "maxOutputTokens": validated_params.get("max_tokens", 4000),
                    "temperature": validated_params.get("temperature", 0.7),
                    "topP": validated_params.get("top_p", 0.9),
                    "topK": validated_params.get("top_k", 40),
                    "stopSequences": validated_params.get("stop", [])
                }
            }
            
            # Make API request
            response_data = self._make_chat_api_request(request_params, request.model or self.default_model)
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Process response
            return self._process_chat_response(
                response_data, request, request_params, response_time_ms, request_id
            )
            
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
        """Create embeddings using Google's embedding model"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Use text-embedding model
            model = "text-embedding-004"
            
            # Prepare request for embedding
            texts = request.texts if hasattr(request, 'texts') else [request.messages[0].get('content', '')]
            
            embeddings = []
            for text in texts:
                request_params = {
                    "model": f"models/{model}",
                    "content": {
                        "parts": [{"text": text}]
                    }
                }
                
                response_data = self._make_embedding_api_request(request_params)
                if "embedding" in response_data:
                    embeddings.append(response_data["embedding"]["values"])
            
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return LLMResponse(
                success=True,
                embeddings=embeddings,
                response_time_ms=response_time_ms,
                model=model,
                provider=self.provider_name,
                request_id=request_id,
                raw_response={"embeddings": embeddings}
            )
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return LLMResponse(
                success=False,
                error_message=str(e),
                response_time_ms=response_time_ms,
                provider=self.provider_name,
                request_id=request_id
            )
    
    def _convert_messages(self, messages):
        gemini_contents = []
        system_instruction = None
        
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            
            if role == "system":
                system_instruction = content
            elif role in ["user", "assistant"]:
                parts = self._convert_content_to_parts(content)
                gemini_role = "user" if role == "user" else "model"
                gemini_contents.append({
                    "role": gemini_role,
                    "parts": parts
                })
        
        # Add system instruction to first user message if present
        if system_instruction and gemini_contents:
            if gemini_contents[0]["role"] == "user":
                system_part = {"text": f"System: {system_instruction}\n\n"}
                gemini_contents[0]["parts"].insert(0, system_part)
        
        return gemini_contents

    def _convert_content_to_parts(self, content):
        """Convert content to Gemini parts format"""
        if isinstance(content, str):
            return [{"text": content}]
        
        if isinstance(content, list):
            parts = []
            for item in content:
                if item.get("type") == "text":
                    parts.append({"text": item.get("text", "")})
                elif item.get("type") == "image_url":
                    url = item.get("image_url", {}).get("url", "")
                    if url.startswith("data:"):
                        # Parse: data:image/jpeg;base64,{base64_data}
                        header, base64_data = url.split(",", 1)
                        mime_type = header.split(":")[1].split(";")[0]
                        
                        parts.append({
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64_data
                            }
                        })
            return parts
        
        return [{"text": str(content)}]
    
    def _make_chat_api_request(self, params: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Make chat completion API request to Google Gemini"""
        headers = {
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/v1beta/models/{model}:generateContent?key={self.api_key}"
        
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
    
    def _make_embedding_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make embedding API request to Google"""
        headers = {
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
        
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
        
        raise APIError(f"Google Gemini API request failed with status {response.status_code}: {error_detail}")
    
    def _process_chat_response(
        self,
        response_data: Dict[str, Any],
        request: LLMRequest,
        request_params: Dict[str, Any],
        response_time_ms: int,
        request_id: str
    ) -> LLMResponse:
        """Process Google Gemini chat completion response"""
        output_text = ""
        
        if "candidates" in response_data and response_data["candidates"]:
            candidate = response_data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if parts and "text" in parts[0]:
                    output_text = parts[0]["text"]
        
        # Process output based on response type
        processed_output = self._process_output_by_type(
            output_text, request.response_type
        )
        
        
        # Extract usage metadata if available
        usage_metadata = response_data.get("usageMetadata", {})
        if usage_metadata:
            input_tokens = usage_metadata.get("promptTokenCount")
            output_tokens = usage_metadata.get("candidatesTokenCount") + usage_metadata.get("thoughtsTokenCount", 0)
            total_tokens = usage_metadata.get("totalTokenCount")
        
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
                cleaned_data = re.sub(r'^```json\s*', '', output_text.strip())
                cleaned_data = re.sub(r'\s*```\s*$', '', cleaned_data)
                return json.loads(cleaned_data)
            except json.JSONDecodeError as e:
                return {
                    "error": f"Failed to parse JSON: {str(e)}",
                    "raw_output": output_text
                }
        else:
            return output_text