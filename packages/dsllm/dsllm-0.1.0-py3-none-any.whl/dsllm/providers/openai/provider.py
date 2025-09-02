"""
OpenAI provider implementation.
"""

import logging
from typing import Any, Optional

import openai
from openai import AsyncOpenAI

from ...exceptions import ProviderError

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """OpenAI LLM provider implementation."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: Model name to use
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI client parameters
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        try:
            self.client = AsyncOpenAI(api_key=api_key, **kwargs)
        except Exception as e:
            raise ProviderError(f"Failed to initialize OpenAI client: {e}") from e
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using OpenAI API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        # Prepare generation parameters with proper types
        generation_params: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        
        # Only add max_tokens if it's not None
        if self.max_tokens is not None:
            generation_params["max_tokens"] = self.max_tokens
            
        # Add any additional kwargs
        generation_params.update(kwargs)
        
        try:
            logger.debug(f"Generating with OpenAI model {self.model}")
            response = await self.client.chat.completions.create(**generation_params)
            
            if not response.choices:
                raise ProviderError("No choices returned from OpenAI API")
            
            content = response.choices[0].message.content
            if content is None:
                raise ProviderError("No content returned from OpenAI API")
            
            return str(content).strip()
            
        except openai.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ProviderError(f"OpenAI API error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during generation: {e}")
            raise ProviderError(f"Unexpected error during generation: {e}") from e
