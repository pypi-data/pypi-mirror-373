"""
LLM Client - Real AI Integration with Token Optimization
Connects to OpenAI, Claude, and other providers with cost optimization
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import openai
from anthropic import Anthropic

# Import requests if available, otherwise skip OpenRouter features
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class LLMClient:
    """LLM client with token optimization and multiple provider support"""
    
    def __init__(self):
        self.config = self._load_config()
        self.current_provider = None
        self.client = None
        self._initialize_client()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from user config file"""
        config_file = Path.home() / ".aider-genius" / "config.json"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration with multiple free model options (verified working)
            return {
                "llm_provider": "openrouter",
                "model": "deepseek/deepseek-chat-v3.1:free",  # Excellent for coding
                "fallback_models": [
                    "qwen/qwen3-coder:free",                        # Specialized for code
                    "openai/gpt-oss-120b:free",                     # Large context
                    "z-ai/glm-4.5-air:free",                        # Fast and reliable  
                    "google/gemma-3n-e2b-it:free",                  # Google's latest
                    "google/gemma-2-9b-it:free"                     # Original fallback
                ],
                "api_base": "https://openrouter.ai/api/v1",
                "max_tokens": 4000,
                "temperature": 0.2,
                "api_key": "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"
            }
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        provider = self.config.get("llm_provider", "openrouter")
        api_key = self.config.get("api_key") or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            print("Warning: No API key found. Set in config or environment variable.")
            return
        
        try:
            if provider == "openrouter":
                # OpenRouter uses OpenAI-compatible API
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url=self.config.get("api_base", "https://openrouter.ai/api/v1")
                )
                self.current_provider = "openrouter"
            elif provider == "openai":
                self.client = openai.OpenAI(api_key=api_key)
                self.current_provider = "openai"
            elif provider == "anthropic":
                self.client = Anthropic(api_key=api_key)
                self.current_provider = "anthropic"
            else:
                print(f"Warning: Unknown provider: {provider}")
                self.client = None
                
        except Exception as e:
            print(f"Warning: Failed to initialize LLM client: {e}")
            self.client = None
            self.current_provider = None
    
    def generate_code(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate code using LLM with token optimization
        
        Args:
            prompt: The coding task description
            context: Additional context (file content, OSP analysis, etc.)
            
        Returns:
            Generated code and metadata
        """
        if not self.client:
            return {
                "success": False,
                "error": "No LLM client available",
                "mock_response": self._generate_mock_response(prompt, context)
            }
        
        try:
            # Optimize prompt using Jac token optimizer
            optimized_prompt = self._optimize_prompt_with_jac(prompt, context)
            
            # Generate code based on provider
            if self.current_provider == "openrouter":
                response = self._call_openrouter(optimized_prompt)
            elif self.current_provider == "openai":
                response = self._call_openai(optimized_prompt)
            elif self.current_provider == "anthropic":
                response = self._call_anthropic(optimized_prompt)
            else:
                response = self._generate_mock_response(prompt, context)
            
            return {
                "success": True,
                "generated_code": response.get("code", ""),
                "explanation": response.get("explanation", ""),
                "token_usage": response.get("tokens", {}),
                "optimized_prompt": optimized_prompt != prompt
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "mock_response": self._generate_mock_response(prompt, context)
            }
    
    def _optimize_prompt_with_jac(self, prompt: str, context: Dict = None) -> str:
        """Use Jac token optimizer to reduce prompt size"""
        try:
            # Use the working token optimizer
            from ..integration.jac_bridge import JacBridge
            bridge = JacBridge(os.path.dirname(__file__))
            
            optimization_result = bridge.call_walker(
                "token_optimizer", "optimize_prompt",
                {"code": prompt}
            )
            
            if optimization_result.get("optimized_code"):
                return optimization_result["optimized_code"]
            else:
                return prompt
                
        except Exception:
            # Fallback: simple optimization
            lines = prompt.split('\n')
            optimized_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            return '\n'.join(optimized_lines)
    
    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            response = self.client.ChatCompletion.create(
                model=self.config.get("model", "gpt-4"),
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Generate clean, efficient code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.get("max_tokens", 4000),
                temperature=self.config.get("temperature", 0.2)
            )
            
            return {
                "code": response.choices[0].message.content,
                "explanation": "Generated by OpenAI",
                "tokens": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=self.config.get("max_tokens", 4000),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "code": response.content[0].text,
                "explanation": "Generated by Claude",
                "tokens": {
                    "prompt": response.usage.input_tokens,
                    "completion": response.usage.output_tokens,
                    "total": response.usage.input_tokens + response.usage.output_tokens
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _call_openrouter(self, prompt: str) -> Dict[str, Any]:
        """Call OpenRouter API with automatic fallback to different free models"""
        # Check if client is properly initialized
        if not self.client:
            return {"error": "LLM client not properly initialized. Check API key and configuration."}
        
        # Get primary model and fallback models
        primary_model = self.config.get("model", "deepseek/deepseek-chat-v3.1:free")
        fallback_models = self.config.get("fallback_models", [
            "deepseek/deepseek-chat-v3.1:free",  # Keep trying DeepSeek first
            "qwen/qwen3-coder:free",
            "z-ai/glm-4.5-air:free", 
            "google/gemma-3n-e2b-it:free",
            "google/gemma-2-9b-it:free"  # Last resort
        ])
        
        models_to_try = [primary_model] + fallback_models
        
        for model in models_to_try:
            try:
                print(f"🤖 Trying model: {model}")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert programmer. Generate clean, efficient code with proper documentation."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=self.config.get("max_tokens", 4000),
                    temperature=self.config.get("temperature", 0.2),
                    extra_headers={
                        "HTTP-Referer": "https://github.com/ThiruvarankanM/Rebuilding-Aider-with-Jac-OSP",
                        "X-Title": "Aider-Genius AI Coding Assistant"
                    }
                )
                
                print(f"✅ Success with model: {model}")
                return {
                    "code": response.choices[0].message.content,
                    "explanation": f"Generated by {model}",
                    "model_used": model,
                    "tokens": {
                        "prompt": response.usage.prompt_tokens if response.usage else 0,
                        "completion": response.usage.completion_tokens if response.usage else 0,
                        "total": response.usage.total_tokens if response.usage else 0
                    }
                }
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Model {model} failed: {error_msg}")
                
                # Check if it's a rate limit or specific error
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    print(f"⚠️ Rate limit hit for {model}, trying next...")
                    continue
                elif "401" in error_msg or "unauthorized" in error_msg.lower():
                    print(f"⚠️ Auth issue with {model}, trying next...")
                    continue
                else:
                    print(f"⚠️ Other error with {model}: {error_msg}")
                    continue
        
        # If all models fail
        return {
            "error": f"All models failed. Last error with {models_to_try[-1]}: {error_msg}",
            "models_tried": models_to_try
        }
    
    def _generate_mock_response(self, prompt: str, context: Dict = None) -> Dict[str, Any]:
        """Generate mock response when no LLM available (for testing)"""
        
        # Intelligent mock based on prompt analysis
        if "error handling" in prompt.lower():
            mock_code = """try:
    # Original code here
    pass
except Exception as e:
    print(f"Error: {e}")
    raise"""
        elif "logging" in prompt.lower():
            mock_code = """import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Operation completed successfully")"""
        elif "docstring" in prompt.lower():
            mock_code = '''"""
Function description here.

Args:
    param1: Description
    
Returns:
    Description of return value
"""'''
        else:
            mock_code = f"# Generated code for: {prompt[:50]}...\n# TODO: Implement actual functionality"
        
        return {
            "code": mock_code,
            "explanation": "Mock response (no API key provided)",
            "tokens": {"estimated": len(prompt) // 4}
        }
    
    def estimate_cost(self, prompt: str) -> Dict[str, Any]:
        """Estimate LLM API cost for prompt"""
        token_count = len(prompt) // 4  # Rough estimation
        
        # Pricing estimates (approximate)
        costs = {
            "openai_gpt4": token_count * 0.00003,  # $0.03/1K tokens
            "anthropic_claude": token_count * 0.000015,  # $0.015/1K tokens
        }
        
        return {
            "estimated_tokens": token_count,
            "estimated_costs": costs,
            "cheapest_provider": min(costs.keys(), key=lambda k: costs[k])
        }
