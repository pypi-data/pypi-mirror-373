from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ModelPricing:
    input_cost_per_1k: float
    output_cost_per_1k: float
    embedding_cost_per_1k: Optional[float] = None
    model_type: str = "chat"
    
    def calculate_cost(self, input_tokens: int = 0, output_tokens: int = 0) -> float:
        """Calculate total cost based on token usage"""
        input_cost = (input_tokens / 1000) * self.input_cost_per_1k
        
        if self.model_type == "embedding":
            # For embedding models, typically only input tokens are charged
            return input_cost
        else:
            # For chat models, both input and output tokens are charged
            output_cost = (output_tokens / 1000) * self.output_cost_per_1k
            return input_cost + output_cost

class CostTracker:
    
    PRICING_DATA = {
        "openai": {
            # GPT-5 Models
            "gpt-5": ModelPricing(0.1087, 0.870),
            # GPT-4 Models
            "gpt-4.1": ModelPricing(0.174, 0.696),
            "gpt-4.1-mini": ModelPricing(0.0348, 0.1392),
            "gpt-4": ModelPricing(2.61, 5.22),
            "gpt-4-32k": ModelPricing(5.22, 10.44),
            "gpt-4-turbo": ModelPricing(0.87, 2.61),
            "gpt-4-turbo-preview": ModelPricing(0.87, 2.61),
            "gpt-4-vision-preview": ModelPricing(0.87, 2.61),
            
            # GPT-4o Models
            "gpt-4o": ModelPricing(0.435, 1.305),
            "gpt-4o-mini": ModelPricing(0.01305, 0.0522),
            
            # GPT-3.5 Models
            "gpt-3.5-turbo": ModelPricing(0.1305, 0.174),
            "gpt-3.5-turbo-16k": ModelPricing(0.261, 0.348),
            
            # Embedding Models
            "text-embedding-ada-002": ModelPricing(0.0087, 0.0, 0.0087, "embedding"),
            "text-embedding-3-small": ModelPricing(0.00174, 0.0, 0.00174, "embedding"),
            "text-embedding-3-large": ModelPricing(0.01131, 0.0, 0.01131, "embedding"),
        },
        
        "azureopenai": {
            "gpt-5": ModelPricing(0.1087, 0.870),
            "gpt-4.1": ModelPricing(0.174, 0.696),
            "gpt-4.1-mini": ModelPricing(0.0348, 0.1392),
            "gpt-4": ModelPricing(2.61, 5.22),
            "gpt-4-32k": ModelPricing(5.22, 10.44),
            "gpt-4-turbo": ModelPricing(0.87, 2.61),
            "gpt-4o": ModelPricing(0.435, 1.305),
            "gpt-4o-mini": ModelPricing(0.01305, 0.0522),
            "gpt-35-turbo": ModelPricing(0.1305, 0.174),
            "phi-4": ModelPricing(0.0108,0.0434),
            "text-embedding-ada-002": ModelPricing(0.0087, 0.0, 0.0087, "embedding"),
        },
        
        "anthropic": {
            # Claude 3 Models
            "claude-3-opus-20240229": ModelPricing(1.305, 6.525),
            "claude-3-sonnet-20240229": ModelPricing(0.261, 1.305),
            "claude-3-haiku-20240307": ModelPricing(0.02175, 0.10875),
            
            # Claude 3.5 Models
            "claude-3-5-sonnet-20241022": ModelPricing(0.261, 1.305),
            "claude-3-5-haiku-20241022": ModelPricing(0.087, 0.435),
            
            # Claude 4 Models (hypothetical pricing based on trends)
            "claude-4-opus": ModelPricing(1.74, 8.7),
            "claude-4-sonnet": ModelPricing(0.6786, 2.088),
        },
        
        "google": {
            "gemini-2.5-pro": ModelPricing(0.10875, 0.87),
            "gemini-2.5-pro-large": ModelPricing(0.2175, 1.305),
            "gemini-2.5-flash": ModelPricing(0.02610, 0.2175),
            "gemini-2.5-flash-lite": ModelPricing(0.0087, 0.0348),
            
            # Gemini 2.0 Models
            "gemini-2.0-flash": ModelPricing(0.0087, 0.0348),
            "gemini-2.0-flash-lite": ModelPricing(0.006525, 0.02610),
            
            # Gemini 1.5 Models
            "gemini-1.5-pro": ModelPricing(0.10875, 0.435),
            "gemini-1.5-pro-large": ModelPricing(0.2175, 0.87),
            "gemini-1.5-flash": ModelPricing(0.006525, 0.02610),
            "gemini-1.5-flash-large": ModelPricing(0.01305, 0.0522),
            "gemini-1.5-flash-8b": ModelPricing(0.00326025, 0.01305),
            "gemini-1.5-flash-8b-large": ModelPricing(0.006525, 0.02610),
            
            # Legacy Gemini Models
            "gemini-pro": ModelPricing(1.89225, 3.7845),
            "gemini-pro-vision": ModelPricing(1.89225, 3.7845),
            "gemini-ultra": ModelPricing(15.138, 45.414),
            
            # Gemma Models
            "gemma-3": ModelPricing(0.0, 0.0),
            "gemma-3n": ModelPricing(0.0, 0.0),
            "gemma-7b": ModelPricing(0.22707, 0.22707),
            "gemma-2b": ModelPricing(0.22707, 0.22707),
            
            # Legacy PaLM Models (keeping existing for compatibility)
            "text-bison": ModelPricing(7.569, 7.569),
            "chat-bison": ModelPricing(3.7845, 3.7845),
            
            # Embedding Models
            "gemini-embedding": ModelPricing(0.01305, 0.0, 0.01305, "embedding"),
            "textembedding-gecko": ModelPricing(0.7569, 0.0, 0.7569, "embedding"),
            
            # Specialized Models (Audio/Image/Video - different pricing structure)
            "gemini-2.5-flash-native-audio": ModelPricing(0.0435, 0.174),
            "gemini-2.5-flash-image-preview": ModelPricing(0.02610, 3.393),
            "gemini-2.5-flash-tts": ModelPricing(0.0435, 0.87),
            "gemini-2.5-pro-tts": ModelPricing(0.087, 1.74),
            
            # Image Generation Models (per image pricing)
            "imagen-4-fast": ModelPricing(0.0, 1.74),
            "imagen-4-standard": ModelPricing(0.0, 3.48),
            "imagen-4-ultra": ModelPricing(0.0, 5.22),
            "imagen-3": ModelPricing(0.0, 2.61),
            
            # Video Generation Models (per second pricing)
            "veo-3": ModelPricing(0.0, 65.25),
            "veo-3-fast": ModelPricing(0.0, 34.8),
            "veo-2": ModelPricing(0.0, 30.45),
        },
        
        "grok": {
            # Grok Models
            "grok-1": ModelPricing(0.28797, 1.43898),
            "grok-2": ModelPricing(0.28797, 1.43898),
            "grok-vision": ModelPricing(0.28797, 1.43898),
        },
        
        "deepseek": {
            # DeepSeek Models (extremely cost-effective)
            "deepseek-chat": ModelPricing(0.02349, 0.0957), 
            "deepseek-chat-cached": ModelPricing(0.00609, 0.0957),
            "deepseek-coder": ModelPricing(0.02349, 0.0957),
            
            # Embedding Models
            "deepseek-embedding": ModelPricing(0.00174, 0.0, 0.00174, "embedding"),
        },
        
        "qwen": {
            # Qwen Models
            "qwen-max": ModelPricing(0.03306, 0.13224),
            "qwen-plus": ModelPricing(0.01653, 0.06612),
            "qwen-turbo": ModelPricing(0.0087, 0.0348),
            
            # Qwen2.5 Models
            "qwen2.5-72b": ModelPricing(0.087, 0.348),
            "qwen2.5-32b": ModelPricing(0.0435, 0.174),
            "qwen2.5-14b": ModelPricing(0.02610, 0.1044),
            
            # Embedding Models
            "qwen-embedding": ModelPricing(0.00435, 0.0, 0.00435, "embedding"),
        },
        "llama": {
            # LLaMA Models (hypothetical pricing)
            "llama-4-Maverick-17B-128E-Instruct-FP8": ModelPricing(0.0234, 0.0739)
        }
    }

    def get_model_pricing(self, provider: str, model: str) -> Optional[ModelPricing]:
        """Get pricing information for a specific model"""
        provider_lower = provider.lower()
        
        if provider_lower not in self.PRICING_DATA:
            logger.warning(f"No pricing dataaaaa available for provider: {provider}")
            return None
            
        model_lower = model.lower() if model else ""
        
        # Try exact match first
        if model_lower in self.PRICING_DATA[provider_lower]:
            return self.PRICING_DATA[provider_lower][model_lower]
        
        # Try partial matching for deployment names (Azure OpenAI case)
        for pricing_model, pricing in self.PRICING_DATA[provider_lower].items():
            if pricing_model in model_lower or model_lower in pricing_model:
                return pricing
        
        logger.warning(f"No pricing data available for model: {model} on provider: {provider}")
        return None
    
    def calculate_request_cost(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int = 0,
        request_type: str = "chat"
    ) -> Tuple[float, Dict[str, Any]]:

        pricing = self.get_model_pricing(provider, model)
        
        if not pricing:
            return 0.0, {
                "error": f"No pricing data for {provider}/{model}",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "estimated_cost": 0.0
            }
        
        total_cost = pricing.calculate_cost(input_tokens, output_tokens)
        
        cost_breakdown = {
            "provider": provider,
            "model": model,
            "request_type": request_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost_per_1k": pricing.input_cost_per_1k,
            "output_cost_per_1k": pricing.output_cost_per_1k,
            "input_cost": (input_tokens / 1000) * pricing.input_cost_per_1k,
            "output_cost": (output_tokens / 1000) * pricing.output_cost_per_1k if request_type != "embedding" else 0.0,
            "total_cost": total_cost,
            "currency": "INR"
        }
        
        return total_cost, cost_breakdown
    
    def track_cost(
        self, 
        provider: str, 
        model: str, 
        input_tokens: int, 
        output_tokens: int = 0,
        request_type: str = "chat"
    ) -> Dict[str, Any]:

        cost, breakdown = self.calculate_request_cost(
            provider, model, input_tokens, output_tokens, request_type
        )
        
        return {
            "current_request_cost": cost,
            "cost_breakdown": breakdown
        }
    
    def add_custom_pricing(
        self, 
        provider: str, 
        model: str, 
        input_cost_per_1k: float, 
        output_cost_per_1k: float,
        model_type: str = "chat"
    ):
        """Add custom pricing for a new model"""
        if provider.lower() not in self.PRICING_DATA:
            self.PRICING_DATA[provider.lower()] = {}
        
        self.PRICING_DATA[provider.lower()][model.lower()] = ModelPricing(
            input_cost_per_1k, output_cost_per_1k, 
            input_cost_per_1k if model_type == "embedding" else None,
            model_type
        )
        
        logger.info(f"Added custom pricing for {provider}/{model}")