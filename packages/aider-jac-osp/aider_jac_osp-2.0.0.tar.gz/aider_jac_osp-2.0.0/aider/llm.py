import importlib
import os
import warnings
from aider.dump import dump  # noqa: F401

# Import new configs/flags
from .args import Args
from .prompts import get_optimized_prompt, get_genius_template
from .repo import get_repo_context
from .models import get_model_for_mode

# Import Jac integration
try:
    from .jac_integration import process_with_jac
    JAC_AVAILABLE = True
except ImportError:
    JAC_AVAILABLE = False

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

AIDER_SITE_URL = "https://aider.chat"
AIDER_APP_NAME = "Aider"
os.environ["OR_SITE_URL"] = AIDER_SITE_URL
os.environ["OR_APP_NAME"] = AIDER_APP_NAME
os.environ["LITELLM_MODE"] = "PRODUCTION"

# `import litellm` takes 1.5 seconds, defer it!
VERBOSE = False

class LazyLiteLLM:
    _lazy_module = None
    
    def __getattr__(self, name):
        if name == "_lazy_module":
            return super()
        self._load_litellm()
        return getattr(self._lazy_module, name)
    
    def _load_litellm(self):
        if self._lazy_module is not None:
            return
        if VERBOSE:
            print("Loading litellm...")
        self._lazy_module = importlib.import_module("litellm")
        self._lazy_module.suppress_debug_info = True
        self._lazy_module.set_verbose = False
        self._lazy_module.drop_params = True
        self._lazy_module._logging._disable_debugging()

# Token optimization layer
def optimize_prompt_for_genius(prompt, context=None):
    """Compress and optimize prompt for genius mode"""
    try:
        # Get genius-optimized template
        optimized_template = get_genius_template()
        
        # Compress boilerplate tokens
        compressed_prompt = prompt.replace("Please help me with", "Help:")
        compressed_prompt = compressed_prompt.replace("I would like you to", "Do:")
        
        # Add repo context if available and within token limits
        if context:
            # Truncate context if too long (rough token estimation)
            if len(context) > 2000:  # ~500 tokens
                context = context[:2000] + "..."
                if VERBOSE:
                    print("Warning: Repo context truncated due to token limits")
            
            compressed_prompt = f"{optimized_template}\n\nContext:\n{context}\n\nTask:\n{compressed_prompt}"
        
        return compressed_prompt
    except Exception as e:
        if VERBOSE:
            print(f"Warning: Genius optimization failed: {e}")
        return prompt  # Fallback to original

def prepare_prompt(prompt, args=None):
    """Main prompt preparation with mode switching"""
    if not args:
        return prompt
    
    # Get repo context if needed
    context = None
    if hasattr(args, 'genius') and args.genius:
        try:
            context = get_repo_context(max_tokens=2000)
        except Exception as e:
            if VERBOSE:
                print(f"Warning: Could not retrieve repo context: {e}")
    
    # Apply genius mode optimization
    if hasattr(args, 'genius') and args.genius:
        prompt = optimize_prompt_for_genius(prompt, context)
    
    # Apply Jac preprocessing if enabled
    if hasattr(args, 'jac') and args.jac and JAC_AVAILABLE:
        try:
            prompt = process_with_jac(prompt, mode='preprocess')
        except Exception as e:
            if VERBOSE:
                print(f"Warning: Jac preprocessing failed: {e}")
            # Continue with non-Jac processing
    
    return prompt

def get_model_for_request(args=None):
    """Dynamic model selection based on mode"""
    if not args:
        return None  # Use default
    
    try:
        if hasattr(args, 'genius') and args.genius:
            return get_model_for_mode('genius')
        elif hasattr(args, 'jac') and args.jac:
            return get_model_for_mode('jac')
        else:
            return get_model_for_mode('default')
    except Exception as e:
        if VERBOSE:
            print(f"Warning: Model selection failed: {e}")
        return None  # Fallback to default

def generate_response(prompt, args=None, **kwargs):
    """Enhanced response generation with mode handling"""
    # Prepare prompt with optimizations
    optimized_prompt = prepare_prompt(prompt, args)
    
    # Get appropriate model
    model = get_model_for_request(args)
    if model:
        kwargs['model'] = model
    
    try:
        # Generate response using LiteLLM
        response = litellm.completion(
            messages=[{"role": "user", "content": optimized_prompt}],
            **kwargs
        )
        
        result = response.choices[0].message.content
        
        # Apply Jac postprocessing if enabled
        if args and hasattr(args, 'jac') and args.jac and JAC_AVAILABLE:
            try:
                result = process_with_jac(result, mode='postprocess')
            except Exception as e:
                if VERBOSE:
                    print(f"Warning: Jac postprocessing failed: {e}")
                # Return result without post-processing
        
        return result
        
    except Exception as e:
        if VERBOSE:
            print(f"Error in generate_response: {e}")
        raise

litellm = LazyLiteLLM()

__all__ = ["litellm", "prepare_prompt", "generate_response", "get_model_for_request"]