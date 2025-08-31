import os
import asyncio
from typing import Dict, Any, List, Optional, AsyncGenerator
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from .base_client import BaseLLMClient, LLMResponse

class GeminiClient(BaseLLMClient):
    def __init__(self, model_name: str = "gemini-2.5-flash", api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings for content generation
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        try:
            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )

            return LLMResponse(
                content=response.text,
                model=self.model_name,
                tokens_used=0,  # Gemini doesn't provide token count
                finish_reason="stop"
            )
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    async def stream_generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        try:
            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40
            )

            # Generate streaming response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt,
                generation_config=generation_config,
                safety_settings=self.safety_settings,
                stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            raise Exception(f"Gemini streaming error: {str(e)}")

    async def generate_with_context(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        try:
            # Convert messages to conversation format
            conversation_text = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    conversation_text += f"System: {content}\n"
                elif role == "user":
                    conversation_text += f"Human: {content}\n"
                elif role == "assistant":
                    conversation_text += f"Assistant: {content}\n"
            
            # Add prompt for next response
            conversation_text += "Assistant: "
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                top_p=0.8,
                top_k=40
            )
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                conversation_text,
                generation_config=generation_config,
                safety_settings=self.safety_settings
            )
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "provider": "Google",
            "max_tokens": 8192,
            "supports_streaming": False,
            "supports_function_calling": True
        }

class GeminiAgentExecutor:
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
    
    async def execute_agent_task(
        self,
        agent_name: str,
        agent_role: str,
        agent_goal: str,
        agent_backstory: str,
        task_description: str,
        context: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        # Extract LLM config
        llm_config = config.get("llm", {}) if config else {}
        temperature = llm_config.get("temperature", 0.7)
        max_tokens = llm_config.get("max_tokens", 2000)
        
        # Build system prompt
        system_prompt = f"""You are {agent_name}, a {agent_role}.
Your goal: {agent_goal}
Your background: {agent_backstory}

You are working on this task: {task_description}

Please provide a comprehensive response that fulfills the task requirements.
Be professional, detailed, and focus on delivering high-quality output."""

        # Add context if provided
        if context:
            system_prompt += f"\n\nAdditional context: {context}"
        
        # Generate response
        response = await self.client.generate_response(
            prompt=task_description,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt
        )
        
        return response

# Factory function for easy integration
def create_gemini_client(model_name: str = "gemini-2.5-flash") -> GeminiClient:
    return GeminiClient(model_name=model_name)

def create_gemini_executor(model_name: str = "gemini-2.5-flash") -> GeminiAgentExecutor:
    client = create_gemini_client(model_name)
    return GeminiAgentExecutor(client)
