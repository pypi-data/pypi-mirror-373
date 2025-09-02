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

class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.service_url = config['service_url'].rstrip('/')
        self.api_key = config['api_key']
        self.deployment_name = config['deployment_name']
        self.api_version = config['api_version']
        self.timeout = config.get('timeout', 600)
        
        # Initialize tokenizer
        self.tokenizer = TokenizerFactory.create_tokenizer('tiktoken')
        
        self.validate_config()
    
    def validate_config(self) -> bool:
        """Validate Azure OpenAI configuration"""
        required_fields = ['service_url', 'api_key', 'deployment_name', 'api_version']
        for field in required_fields:
            if not self.config.get(field):
                raise ConfigurationError(f"Missing required field: {field}")
        return True
    
    def send_chat_completion(self, request: LLMRequest) -> LLMResponse:
        """Send chat completion request to Azure OpenAI"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Validate and prepare parameters
            validated_params = ParameterValidator.validate_parameters(
                request.parameters, 'openai'
            )
            
            # Prepare request payload
            request_params = {
                "messages": request.messages,
                "model": request.model or self.deployment_name,
                **validated_params
            }
            
            # Handle JSON response format
            if request.response_type == ResponseType.JSON:
                request_params["response_format"] = {"type": "json_object"}
                self._ensure_json_instruction(request_params["messages"])
            
            # Make API request
            response_data = self._make_chat_api_request(request_params)
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
                model=request.model,
                provider=self.provider_name,
                request_id=request_id
            )
    
    def create_embeddings(self, request: LLMRequest) -> LLMResponse:
        """Create embeddings using Azure OpenAI"""
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        try:
            # Normalize input to list
            if isinstance(request.input_texts, str):
                input_list = [request.input_texts]
                single_input = True
            else:
                input_list = request.input_texts
                single_input = False
            
            # Validate input
            if not input_list or any(not text.strip() for text in input_list):
                raise APIError("Input texts cannot be empty")
            
            # Prepare request payload
            request_params = {
                "input": input_list,
                **request.parameters
            }
            
            # Make API request
            response_data = self._make_embedding_api_request(
                request_params, request.model or "text-embedding-ada-002"
            )
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Process response
            return self._process_embedding_response(
                response_data, request, input_list, response_time_ms, request_id, single_input
            )
            
        except Exception as e:
            end_time = time.time()
            response_time_ms = int((end_time - start_time) * 1000)
            
            return LLMResponse(
                success=False,
                error_message=str(e),
                response_time_ms=response_time_ms,
                model=request.model,
                provider=self.provider_name,
                request_id=request_id
            )
    
    def _make_chat_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make chat completion API request"""
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        url = f"{self.service_url}/openai/deployments/{self.deployment_name}/chat/completions"
        query_params = {"api-version": self.api_version}
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                params=query_params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self._handle_api_error(response)
                
        except requests.RequestException as e:
            raise APIError(f"HTTP request failed: {e}")
    
    def _make_embedding_api_request(self, params: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Make embedding API request"""
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        url = f"{self.service_url}/openai/deployments/{model}/embeddings"
        query_params = {"api-version": self.api_version}
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                params=query_params,
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
        
        raise APIError(f"Azure OpenAI API request failed with status {response.status_code}: {error_detail}")
    
    def _process_chat_response(
        self, 
        response_data: Dict[str, Any], 
        request: LLMRequest, 
        request_params: Dict[str, Any],
        response_time_ms: int,
        request_id: str
    ) -> LLMResponse:
        """Process chat completion response"""
        output_text = ""
        if "choices" in response_data and response_data["choices"]:
            choice = response_data["choices"][0]
            if "message" in choice:
                output_text = choice["message"].get("content", "")
        
        # Process output based on response type
        processed_output = self._process_output_by_type(
            output_text, request.response_type
        )
        
        # Calculate tokens
        input_text = self._extract_text_from_messages(request.messages)
        input_tokens = self.tokenizer.count_tokens(input_text, request.model)
        output_tokens = self.tokenizer.count_tokens(output_text, request.model)
        total_tokens = input_tokens + output_tokens
        
        return LLMResponse(
            success=True,
            output_text=output_text,
            processed_output=processed_output,
            token_usage=TokenUsage(input_tokens, output_tokens, total_tokens),
            response_time_ms=response_time_ms,
            model=request.model,
            provider=self.provider_name,
            request_id=request_id,
            raw_response=response_data
        )
    
    def _process_embedding_response(
        self,
        response_data: Dict[str, Any],
        request: LLMRequest,
        input_texts: List[str],
        response_time_ms: int,
        request_id: str,
        single_input: bool
    ) -> LLMResponse:
        """Process embedding response"""
        embeddings = []
        if "data" in response_data:
            for item in response_data["data"]:
                if "embedding" in item:
                    embeddings.append(item["embedding"])
        
        if not embeddings:
            raise APIError("No embeddings found in response")
        
        # Calculate tokens
        total_input_text = " ".join(input_texts)
        input_tokens = self.tokenizer.count_tokens(total_input_text, request.model)
        
        return LLMResponse(
            success=True,
            embeddings=embeddings[0] if single_input else embeddings,
            token_usage=TokenUsage(input_tokens, 0, input_tokens),
            response_time_ms=response_time_ms,
            model=request.model,
            provider=self.provider_name,
            request_id=request_id,
            raw_response=response_data,
            metadata={
                "embedding_count": len(embeddings),
                "input_text_count": len(input_texts)
            }
        )
    
    def _ensure_json_instruction(self, messages: List[Dict[str, Any]]) -> None:
        """Ensure JSON instruction is present in messages"""
        if not self._has_json_instruction(messages):
            self._add_json_instruction(messages)
    
    def _has_json_instruction(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if any message contains JSON instruction"""
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str) and "json" in content.lower():
                return True
            elif isinstance(content, list):
                for item in content:
                    if item.get("type") == "text" and "json" in item.get("text", "").lower():
                        return True
        return False
    
    def _add_json_instruction(self, messages: List[Dict[str, Any]]) -> None:
        """Add JSON instruction to the last user message"""
        json_instruction = "\n\nPlease respond with valid JSON format."
        
        for i in reversed(range(len(messages))):
            if messages[i].get("role") == "user":
                content = messages[i].get("content", "")
                
                if isinstance(content, str):
                    messages[i]["content"] += json_instruction
                elif isinstance(content, list):
                    text_added = False
                    for item in reversed(content):
                        if item.get("type") == "text":
                            item["text"] += json_instruction
                            text_added = True
                            break
                    
                    if not text_added:
                        content.append({
                            "type": "text",
                            "text": json_instruction
                        })
                break
    
    def _extract_text_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        """Extract text content from messages for token calculation"""
        text_parts = []
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if isinstance(content, str):
                text_parts.append(f"{role}: {content}")
            elif isinstance(content, list):
                text_content = []
                for item in content:
                    if item.get("type") == "text":
                        text_content.append(item.get("text", ""))
                    elif item.get("type") == "image_url":
                        text_content.append("[IMAGE]")
                
                if text_content:
                    text_parts.append(f"{role}: {' '.join(text_content)}")
        
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