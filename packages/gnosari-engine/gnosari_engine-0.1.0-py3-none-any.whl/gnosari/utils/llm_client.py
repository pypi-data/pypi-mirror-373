import os
import logging
from typing import Optional, Union
import instructor
import openai
from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)

class LLMClientWrapper:
    """Wrapper for creating instructor clients that work with multiple LLM providers."""
    
    # Mapping of model prefixes to their API keys and base URLs
    PROVIDER_CONFIGS = {
        "gpt-": {
            "api_key_env": "OPENAI_API_KEY",
            "base_url": None,  # Use default OpenAI URL
            "provider": "openai"
        },
        "deepseek-": {
            "api_key_env": "DEEPSEEK_API_KEY", 
            "base_url": "https://api.deepseek.com/v1",
            "provider": "deepseek"
        },
        "claude-": {
            "api_key_env": "ANTHROPIC_API_KEY",
            "base_url": "https://api.anthropic.com/v1",
            "provider": "anthropic"
        },
        "gemini-": {
            "api_key_env": "GOOGLE_API_KEY",
            "base_url": "https://generativelanguage.googleapis.com/v1",
            "provider": "google"
        },
        "command-": {
            "api_key_env": "COHERE_API_KEY",
            "base_url": "https://api.cohere.ai/v1",
            "provider": "cohere"
        },
        "together-": {
            "api_key_env": "TOGETHER_API_KEY",
            "base_url": "https://api.together.xyz/v1",
            "provider": "together"
        },
        "llama-": {
            "api_key_env": "TOGETHER_API_KEY",  # Together AI hosts many Llama models
            "base_url": "https://api.together.xyz/v1",
            "provider": "together"
        },
        "mixtral-": {
            "api_key_env": "MISTRAL_API_KEY",
            "base_url": "https://api.mistral.ai/v1",
            "provider": "mistral"
        },
        "mistral-": {
            "api_key_env": "MISTRAL_API_KEY",
            "base_url": "https://api.mistral.ai/v1",
            "provider": "mistral"
        },
        "pplx-": {
            "api_key_env": "PERPLEXITY_API_KEY",
            "base_url": "https://api.perplexity.ai/v1",
            "provider": "perplexity"
        }
    }
    
    @classmethod
    def get_provider_config(cls, model: str) -> Optional[dict]:
        """Get provider configuration for a given model.
        
        Args:
            model: Model name (e.g., "gpt-4o", "deepseek-chat", "claude-3-sonnet")
            
        Returns:
            Provider configuration dict or None if not found
        """
        for prefix, config in cls.PROVIDER_CONFIGS.items():
            if model.startswith(prefix):
                return config
        return None
    
    @classmethod
    def get_api_key(cls, model: str) -> Optional[str]:
        """Get API key for a given model.
        
        Args:
            model: Model name
            
        Returns:
            API key string or None if not found
        """
        config = cls.get_provider_config(model)
        if not config:
            logger.warning(f"No provider configuration found for model: {model}")
            return None
            
        api_key = os.getenv(config["api_key_env"])
        if not api_key:
            logger.warning(f"API key not found for {config['provider']}. Set {config['api_key_env']} environment variable.")
            return None
            
        return api_key
    
    @classmethod
    def create_client(cls, model: str, async_client: bool = False) -> Union[instructor.Instructor, instructor.AsyncInstructor]:
        """Create an instructor client for the specified model.
        
        Args:
            model: Model name (e.g., "gpt-4o", "deepseek-chat", "claude-3-sonnet")
            async_client: Whether to create an async client
            
        Returns:
            Instructor client instance
            
        Raises:
            ValueError: If no provider configuration is found or API key is missing
        """
        config = cls.get_provider_config(model)
        if not config:
            raise ValueError(f"No provider configuration found for model: {model}")
        
        api_key = cls.get_api_key(model)
        if not api_key:
            raise ValueError(f"API key not found for {config['provider']}. Set {config['api_key_env']} environment variable.")
        
        # Create client kwargs
        client_kwargs = {"api_key": api_key}
        
        # Add base URL if specified
        if config["base_url"]:
            client_kwargs["base_url"] = config["base_url"]
        
        # Create the appropriate client
        if async_client:
            openai_client = AsyncOpenAI(**client_kwargs)
        else:
            openai_client = OpenAI(**client_kwargs)
        
        # Create instructor client
        instructor_client = instructor.from_openai(openai_client)
        
        logger.info(f"Created {config['provider']} client for model: {model}")
        return instructor_client
    
    @classmethod
    def list_supported_providers(cls) -> list:
        """List all supported LLM providers.
        
        Returns:
            List of provider names
        """
        return list(set(config["provider"] for config in cls.PROVIDER_CONFIGS.values()))
    
    @classmethod
    def list_supported_models(cls) -> dict:
        """List supported models by provider.
        
        Returns:
            Dictionary mapping provider names to example models
        """
        models_by_provider = {}
        for prefix, config in cls.PROVIDER_CONFIGS.items():
            provider = config["provider"]
            if provider not in models_by_provider:
                models_by_provider[provider] = []
            models_by_provider[provider].append(f"{prefix}*")
        
        return models_by_provider
