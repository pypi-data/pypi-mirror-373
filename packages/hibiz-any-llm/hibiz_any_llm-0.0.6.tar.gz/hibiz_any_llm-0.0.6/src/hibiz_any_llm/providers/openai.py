from typing import Dict, Any
import requests
from .azure_openai import AzureOpenAIProvider
from ..core.exceptions import ConfigurationError

class OpenAIProvider(AzureOpenAIProvider):
    """OpenAI provider implementation (inherits from Azure OpenAI with modifications)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config['api_key']
        self.organization_id = config.get('organization_id')
        self.base_url = config.get('base_url', 'https://api.openai.com/')
        self.timeout = config.get('timeout', 600)
        self.provider_name = 'openai'
        
        # Initialize tokenizer
        from ..utils.tokenizer import TokenizerFactory
        self.tokenizer = TokenizerFactory.create_tokenizer('tiktoken')
        
        self.validate_config()
    
    def validate_config(self) -> bool:
        """Validate OpenAI configuration"""
        if not self.config.get('api_key'):
            raise ConfigurationError("Missing required field: api_key")
        return True
    
    def _make_chat_api_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make chat completion API request to OpenAI"""
        print ("inside make api req")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.organization_id:
            headers["OpenAI-Organization"] = self.organization_id
        
        url = f"{self.base_url}v1/chat/completions"

        print("Params",params)
        
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
            from ..core.exceptions import APIError
            raise APIError(f"HTTP request failed: {e}")
    
    def _make_embedding_api_request(self, params: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Make embedding API request to OpenAI"""
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.organization_id:
            headers["OpenAI-Organization"] = self.organization_id
        
        # Add model to params for OpenAI API
        params["model"] = model
        
        url = f"{self.base_url}/embeddings"
        
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
            from ..core.exceptions import APIError
            raise APIError(f"HTTP request failed: {e}")