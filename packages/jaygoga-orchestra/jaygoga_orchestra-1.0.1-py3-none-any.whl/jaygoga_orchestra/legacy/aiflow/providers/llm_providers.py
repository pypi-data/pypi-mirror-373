"""
Real LLM provider implementations for AIFlow.

Contains actual implementations for OpenAI, Google Gemini, and Anthropic providers.
"""

import os
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass
import aiohttp
import json

# Import actual LLM SDKs
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


@dataclass
class LLMResponse:
    """Standard response format from LLM providers."""
    content: str
    tokens_used: int = 0
    provider: str = ""
    model: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""
    
    def __init__(self, model: str, api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        raise NotImplementedError("Subclasses must implement generate method")
    
    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate a streaming response from the LLM."""
        raise NotImplementedError("Subclasses must implement stream_generate method")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        super().__init__(model, api_key)
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
        
        # Initialize OpenAI client
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                provider="openai",
                model=self.model,
                metadata={"finish_reason": response.choices[0].finish_reason}
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate streaming response using OpenAI API."""
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            content = ""
            tokens_used = 0
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    chunk_content = chunk.choices[0].delta.content
                    content += chunk_content
                    tokens_used += 1  # Approximate token count
                    
                    if stream_callback:
                        await stream_callback(chunk_content)
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                provider="openai",
                model=self.model
            )
            
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {str(e)}")


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, model: str = "gemini-2.0-flash-exp", api_key: Optional[str] = None):
        super().__init__(model, api_key)
        
        if not GEMINI_AVAILABLE:
            raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
        
        # Configure Gemini
        genai.configure(api_key=api_key or os.getenv("GOOGLE_API_KEY"))
        self.client = genai.GenerativeModel(model)
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Gemini API."""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
            
            response = await self.client.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            content = response.text
            tokens_used = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else len(content.split())
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                provider="gemini",
                model=self.model
            )
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate streaming response using Gemini API."""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
            
            response = await self.client.generate_content_async(
                prompt,
                generation_config=generation_config,
                stream=True
            )
            
            content = ""
            tokens_used = 0
            
            async for chunk in response:
                if chunk.text:
                    content += chunk.text
                    tokens_used += len(chunk.text.split())
                    
                    if stream_callback:
                        await stream_callback(chunk.text)
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                provider="gemini",
                model=self.model
            )
            
        except Exception as e:
            raise Exception(f"Gemini streaming error: {str(e)}")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation."""
    
    def __init__(self, model: str = "claude-3-5-haiku-20241022", api_key: Optional[str] = None):
        super().__init__(model, api_key)
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")
        
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic API."""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                provider="anthropic",
                model=self.model,
                metadata={"stop_reason": response.stop_reason}
            )
            
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate streaming response using Anthropic API."""
        try:
            stream = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                **kwargs
            )
            
            content = ""
            tokens_used = 0
            
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    chunk_text = chunk.delta.text
                    content += chunk_text
                    tokens_used += len(chunk_text.split())
                    
                    if stream_callback:
                        await stream_callback(chunk_text)
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                provider="anthropic",
                model=self.model
            )
            
        except Exception as e:
            raise Exception(f"Anthropic streaming error: {str(e)}")


# Provider registry
PROVIDERS = {
    # OpenAI models - Latest 2024/2025
    # GPT-5 series (2025)
    "gpt-5": OpenAIProvider,
    "gpt-5-chat": OpenAIProvider,

    # GPT-4 series (2024/2025)
    "gpt-4.5": OpenAIProvider,
    "gpt-4.1": OpenAIProvider,
    "gpt-4o": OpenAIProvider,
    "gpt-4o-mini": OpenAIProvider,
    "gpt-4-turbo": OpenAIProvider,
    "gpt-4": OpenAIProvider,

    # O1 reasoning series
    "o1": OpenAIProvider,
    "o1-mini": OpenAIProvider,
    "o1-preview": OpenAIProvider,

    # GPT-3.5 series
    "gpt-3.5-turbo": OpenAIProvider,

    # Specialized models
    "chatgpt-4o-latest": OpenAIProvider,

    # Google Gemini models - Latest 2024/2025
    # Gemini 2.x series (2024/2025)
    "gemini-2.5-pro": GeminiProvider,
    "gemini-2.0-flash-exp": GeminiProvider,
    "gemini-2.0-pro": GeminiProvider,
    "gemini-2.0-flash": GeminiProvider,
    "gemini-2.0-flash-lite": GeminiProvider,

    # Gemini 1.5 series
    "gemini-1.5-pro": GeminiProvider,
    "gemini-1.5-flash": GeminiProvider,
    "gemini-1.5-flash-8b": GeminiProvider,

    # Legacy models
    "gemini-pro": GeminiProvider,
    "gemini-pro-vision": GeminiProvider,

    # Anthropic Claude models - Latest 2024/2025
    # Claude 4 series (2025)
    "claude-4.1": AnthropicProvider,
    "claude-4-opus": AnthropicProvider,
    "claude-4-sonnet": AnthropicProvider,

    # Claude 3.7 series (2025)
    "claude-3.7-sonnet": AnthropicProvider,
    "claude-3.7-sonnet-extended-thinking": AnthropicProvider,

    # Claude 3.5 series (2024)
    "claude-3-5-sonnet-20241022": AnthropicProvider,
    "claude-3-5-haiku-20241022": AnthropicProvider,
    "claude-3-5-sonnet-20240620": AnthropicProvider,

    # Claude 3 series
    "claude-3-opus-20240229": AnthropicProvider,
    "claude-3-sonnet-20240229": AnthropicProvider,
    "claude-3-haiku-20240307": AnthropicProvider,
}


def get_provider(model: str, api_key: Optional[str] = None) -> BaseLLMProvider:
    """
    Get an LLM provider instance for the specified model.
    
    Args:
        model: Model name (e.g., 'gpt-4o', 'gemini-2.0-flash-exp', 'claude-3-5-sonnet-20241022')
        api_key: Optional API key (will use environment variables if not provided)
        
    Returns:
        Configured LLM provider instance
        
    Raises:
        ValueError: If model is not supported
    """
    if model not in PROVIDERS:
        available_models = list(PROVIDERS.keys())
        raise ValueError(f"Model '{model}' not supported. Available models: {available_models}")
    
    provider_class = PROVIDERS[model]
    return provider_class(model=model, api_key=api_key)


def list_available_models() -> Dict[str, list]:
    """List all available models by provider."""
    return {
        "openai": [model for model in PROVIDERS.keys() if any(x in model for x in ["gpt", "o1", "chatgpt"])],
        "google": [model for model in PROVIDERS.keys() if "gemini" in model],
        "anthropic": [model for model in PROVIDERS.keys() if "claude" in model],
    }

def get_latest_models() -> Dict[str, str]:
    """Get the latest recommended model for each provider."""
    return {
        "openai": "gpt-4o",  # Most balanced latest model
        "google": "gemini-2.0-flash-exp",  # Latest experimental model
        "anthropic": "claude-3-5-sonnet-20241022",  # Latest stable model
    }

def get_model_info(model: str) -> Dict[str, str]:
    """Get information about a specific model."""
    model_info = {
        # OpenAI GPT-5 series
        "gpt-5": {"provider": "openai", "type": "flagship", "release": "2025", "context": "400K"},
        "gpt-5-chat": {"provider": "openai", "type": "chat", "release": "2025", "context": "128K"},

        # OpenAI GPT-4 series
        "gpt-4.5": {"provider": "openai", "type": "advanced", "release": "2025", "context": "128K"},
        "gpt-4.1": {"provider": "openai", "type": "advanced", "release": "2025", "context": "1M"},
        "gpt-4o": {"provider": "openai", "type": "multimodal", "release": "2024", "context": "128K"},
        "gpt-4o-mini": {"provider": "openai", "type": "efficient", "release": "2024", "context": "128K"},

        # Google Gemini series
        "gemini-2.5-pro": {"provider": "google", "type": "flagship", "release": "2025", "context": "1M"},
        "gemini-2.0-flash-exp": {"provider": "google", "type": "experimental", "release": "2024", "context": "1M"},
        "gemini-1.5-pro": {"provider": "google", "type": "advanced", "release": "2024", "context": "2M"},

        # Anthropic Claude series
        "claude-4-opus": {"provider": "anthropic", "type": "flagship", "release": "2025", "context": "200K"},
        "claude-3-5-sonnet-20241022": {"provider": "anthropic", "type": "balanced", "release": "2024", "context": "200K"},
        "claude-3-5-haiku-20241022": {"provider": "anthropic", "type": "fast", "release": "2024", "context": "200K"},
    }

    return model_info.get(model, {"provider": "unknown", "type": "unknown", "release": "unknown", "context": "unknown"})
