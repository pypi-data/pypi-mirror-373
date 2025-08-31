from typing import Optional, Dict, Any
from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .groq_client import GroqClient
from .gemini_client import GeminiClient

class LLMFactory:
    """Factory for creating LLM clients based on model names."""
    
    # Model mappings
    OPENAI_MODELS = [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
    ]
    
    ANTHROPIC_MODELS = [
        "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", 
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
    ]
    
    GROQ_MODELS = [
        "llama-3.1-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768",
        "gemma-7b-it", "gemma2-9b-it"
    ]
    
    GEMINI_MODELS = [
        "gemini-2.5-flash", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"
    ]
    
    @classmethod
    def create_client(
        cls, 
        model_name: str, 
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseLLMClient:
        """Create appropriate LLM client based on model name."""
        
        # Determine provider based on model name
        if model_name in cls.OPENAI_MODELS or "gpt" in model_name.lower():
            return OpenAIClient(model_name=model_name, api_key=api_key)
        
        elif model_name in cls.ANTHROPIC_MODELS or "claude" in model_name.lower():
            return AnthropicClient(model_name=model_name, api_key=api_key)
        
        elif model_name in cls.GROQ_MODELS or any(x in model_name.lower() for x in ["llama", "mixtral", "gemma"]):
            return GroqClient(model_name=model_name, api_key=api_key)
        
        elif model_name in cls.GEMINI_MODELS or "gemini" in model_name.lower():
            return GeminiClient(model_name=model_name, api_key=api_key)
        
        else:
            # Default to OpenAI for unknown models
            return OpenAIClient(model_name=model_name, api_key=api_key)
    
    @classmethod
    def get_available_models(cls) -> Dict[str, list]:
        """Get all available models by provider."""
        return {
            "openai": cls.OPENAI_MODELS,
            "anthropic": cls.ANTHROPIC_MODELS,
            "groq": cls.GROQ_MODELS,
            "gemini": cls.GEMINI_MODELS
        }
    
    @classmethod
    def get_provider_for_model(cls, model_name: str) -> str:
        """Get provider name for a given model."""
        if model_name in cls.OPENAI_MODELS or "gpt" in model_name.lower():
            return "openai"
        elif model_name in cls.ANTHROPIC_MODELS or "claude" in model_name.lower():
            return "anthropic"
        elif model_name in cls.GROQ_MODELS or any(x in model_name.lower() for x in ["llama", "mixtral", "gemma"]):
            return "groq"
        elif model_name in cls.GEMINI_MODELS or "gemini" in model_name.lower():
            return "gemini"
        else:
            return "openai"  # default

# Convenience functions
def create_llm_client(model_name: str, api_key: Optional[str] = None) -> BaseLLMClient:
    """Create LLM client for the specified model."""
    return LLMFactory.create_client(model_name, api_key)

def get_available_models() -> Dict[str, list]:
    """Get all available models."""
    return LLMFactory.get_available_models()
