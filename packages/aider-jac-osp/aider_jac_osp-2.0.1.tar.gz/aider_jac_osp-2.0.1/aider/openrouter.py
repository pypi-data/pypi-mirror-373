"""
OpenRouter model manager for accessing various AI models
"""

import requests
from typing import Dict, List, Optional, Any


class OpenRouterModelManager:
    """Manages OpenRouter API integration for accessing various AI models"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self._models_cache = None
        
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        if self._models_cache:
            return self._models_cache
            
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                timeout=10
            )
            if response.status_code == 200:
                self._models_cache = response.json().get('data', [])
                return self._models_cache
        except Exception:
            pass
            
        # Return some default models if API call fails
        return [
            {"id": "anthropic/claude-3-5-sonnet", "name": "Claude 3.5 Sonnet"},
            {"id": "openai/gpt-4o", "name": "GPT-4o"},
            {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "google/gemini-pro", "name": "Gemini Pro"}
        ]
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a specific model"""
        models = self.get_available_models()
        for model in models:
            if model.get('id') == model_id:
                return model
        return None
        
    def is_model_available(self, model_id: str) -> bool:
        """Check if a model is available"""
        return self.get_model_info(model_id) is not None
