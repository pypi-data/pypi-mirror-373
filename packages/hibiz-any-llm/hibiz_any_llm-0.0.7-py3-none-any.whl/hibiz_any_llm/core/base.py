import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from .factory import LLMProviderFactory
from ..utils.constants import LLMProvider
from ..models.request import LLMRequest, RequestType, ResponseType
from ..models.response import LLMResponse
from ..database.manager import DatabaseManager
from ..utils.validators import ParameterValidator
from .exceptions import DatabaseError
from .cost_tracker import CostTracker

logger = logging.getLogger(__name__)

class LLMWrapper:
    
    def __init__(
        self,
        provider_type: LLMProvider,
        provider_config: Dict[str, Any],
        db_config: Dict[str, Any],
        enable_logging: bool = True,
        enable_cost_tracking: bool = True
    ):
        self.provider_type = provider_type
        self.provider_config = provider_config
        self.enable_logging = enable_logging
        self.enable_cost_tracking = enable_cost_tracking
        
        # Initialize provider
        self.provider = LLMProviderFactory.create_provider(provider_type, provider_config)
        
        # Initialize cost tracker
        if enable_cost_tracking:
            self.cost_tracker = CostTracker()
            logger.info("Cost tracker initialized successfully")

        self.db_manager = None
        if enable_logging:
            try:
                self.db_manager = DatabaseManager(db_config)
                self.db_manager.create_tables()
                logger.info("Database manager initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize database manager: {e}")
                self.enable_logging = False

    def _extract_text_from_messages(self, messages: List[Dict[str, Any]]) -> str:
        text_parts = []
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            text_parts.append(f"{role}: {content}")
        
        return "\n".join(text_parts)
    
    def send_request(
        self,
        prompt_payload: List[Dict[str, Any]],
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model: Optional[str] = None,
        response_type: str = "text",
        **kwargs
    ) -> Dict[str, Any]:

        request = LLMRequest(
            customer_id=customer_id,
            organization_id=organization_id,
            app_name=app_name,
            module_name=module_name,
            function_name=function_name,
            request_type=RequestType.CHAT_COMPLETION,
            model=model,
            messages=prompt_payload,
            response_type=ResponseType(response_type.lower()),
            parameters=kwargs
        )
        
        # Validate request
        ParameterValidator.validate_request(request)
        
        # Send request through provider
        response = self.provider.send_chat_completion(request)
        print("Provider Name:", self.provider.get_provider_name())

        # Cost estimation before sending request
        cost_estimate = None
        if self.enable_cost_tracking:
            
            cost_estimate = self.cost_tracker.track_cost(
                provider=self.provider.get_provider_name(),
                model=model or self.provider_config.get('default_model', ''),
                input_tokens=response.token_usage.input_tokens if response.token_usage else 0,
                output_tokens=response.token_usage.output_tokens if response.token_usage else 0
            )
        # Log to database if enabled
        if self.enable_logging and self.db_manager:
            self._log_response_with_cost(request, response, cost_estimate)
        
        # Convert response to legacy format with cost information
        legacy_response = self._convert_response_to_legacy_format(response)
        return legacy_response
    
    def create_embeddings(
        self,
        input_texts: Union[str, List[str]],
        customer_id: str,
        organization_id: str,
        app_name: str,
        module_name: str,
        function_name: str,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create embeddings with cost tracking"""
        
        # Create standardized request
        request = LLMRequest(
            customer_id=customer_id,
            organization_id=organization_id,
            app_name=app_name,
            module_name=module_name,
            function_name=function_name,
            request_type=RequestType.EMBEDDING,
            model=model,
            input_texts=input_texts,
            parameters=kwargs
        )
        
        # Validate request
        ParameterValidator.validate_request(request)
        
        # Send request through provider
        response = self.provider.create_embeddings(request)
        
        # Track actual costs
        cost_info = None
        if self.enable_cost_tracking and response.success:
            cost_info = self.cost_tracker.track_cost(
                provider=self.provider.get_provider_name(),
                model=model or self.provider_config.get('default_embedding_model', ''),
                input_tokens=response.token_usage.input_tokens if response.token_usage else 0,
                output_tokens=0,
                request_type="embedding"
            )
        
        # Log to database if enabled
        if self.enable_logging and self.db_manager:
            self._log_response_with_cost(request, response, cost_info)
        
        # Convert response to legacy format
        legacy_response = self._convert_embedding_response_to_legacy_format(response)

        # Cost estimation before sending request
        cost_estimate = None
        if self.enable_cost_tracking:            
            cost_estimate = self.cost_tracker.track_cost(
                provider=self.provider.get_provider_name(),
                model=model or self.provider_config.get('default_embedding_model', ''),
                input_tokens=response.token_usage.input_tokens if response.token_usage else 0,
                output_tokens=0,
                request_type="embedding"
            )
        
        # Add cost information to response
        if cost_info:
            legacy_response.update({
                "cost_estimate": cost_estimate,
                "actual_cost": cost_info["current_request_cost"],
                "cost_breakdown": cost_info["cost_breakdown"]
            })
        
        return legacy_response
    
    def get_usage_stats(
        self,
        customer_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        app_name: Optional[str] = None,
        module_name: Optional[str] = None,
        function_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        request_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.db_manager:
            raise DatabaseError("Database manager not initialized")
        
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        filters = {}
        if app_name:
            filters["app_name"] = app_name
        if module_name:
            filters["module_name"] = module_name
        if function_name:
            filters["function_name"] = function_name
        if request_type:
            filters["request_type"] = request_type
        
        return self.db_manager.get_usage_stats(
            customer_id=customer_id,
            organization_id=organization_id,
            provider=self.provider.get_provider_name(),
            start_date=start_dt,
            end_date=end_dt,
            filters=filters
        )
    
    def _log_response_with_cost(self, request: LLMRequest, response: LLMResponse, cost_info: Optional[Dict[str, Any]]) -> None:
        try:
            log_data = {
                "customer_id": request.customer_id,
                "organization_id": request.organization_id,
                "provider": self.provider.get_provider_name(),
                "model_name": response.model or request.model,
                "app_name": request.app_name,
                "module_name": request.module_name,
                "function_name": request.function_name,
                "request_type": request.request_type.value,
                "request_params": {
                    **request.parameters,
                    "messages": request.messages if request.messages else None,
                    "input_texts": request.input_texts if request.input_texts else None,
                },
                "response_params": response.raw_response,
                "input_tokens": response.token_usage.input_tokens if response.token_usage else 0,
                "output_tokens": response.token_usage.output_tokens if response.token_usage else 0,
                "total_tokens": response.token_usage.total_tokens if response.token_usage else 0,
                "response_time_ms": response.response_time_ms,
                "status": "success" if response.success else "failed",
                "request_id": response.request_id,
                "cost_info": cost_info

            }
            
            self.db_manager.log_token_usage(log_data)
            
        except Exception as e:
            logger.error(f"Failed to log response: {e}")
    
    def _convert_response_to_legacy_format(self, response: LLMResponse) -> Dict[str, Any]:
        """Convert new response format to legacy format for backward compatibility"""
        return {
            "output_text": response.output_text,
            "processed_output": response.processed_output,
            "response_type": response.metadata.get("response_type", "text"),
            "input_tokens": response.token_usage.input_tokens if response.token_usage else 0,
            "output_tokens": response.token_usage.output_tokens if response.token_usage else 0,
            "total_tokens": response.token_usage.total_tokens if response.token_usage else 0,
            "response_time_ms": response.response_time_ms,
            "model": response.model,
            "success": response.success,
            "error_message": response.error_message,
            "full_response": response.raw_response,
            "request_id": response.request_id
        }
    
    def _convert_embedding_response_to_legacy_format(self, response: LLMResponse) -> Dict[str, Any]:
        """Convert embedding response to legacy format"""
        return {
            "embeddings": response.embeddings,
            "input_tokens": response.token_usage.input_tokens if response.token_usage else 0,
            "output_tokens": response.token_usage.output_tokens if response.token_usage else 0,
            "total_tokens": response.token_usage.total_tokens if response.token_usage else 0,
            "response_time_ms": response.response_time_ms,
            "model": response.model,
            "success": response.success,
            "error_message": response.error_message,
            "embedding_count": response.metadata.get("embedding_count", 0),
            "input_text_count": response.metadata.get("input_text_count", 0),
            "request_id": response.request_id
        }
    
    def close(self):
        """Close all connections"""
        if self.db_manager:
            self.db_manager.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()	