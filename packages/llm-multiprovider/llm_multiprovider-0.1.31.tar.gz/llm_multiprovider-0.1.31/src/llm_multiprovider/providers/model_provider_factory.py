import os
import asyncio
from typing import Type, Dict
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.providers.cerebras import CerebrasProvider
from llm_multiprovider.providers.groq import GroqProvider
from llm_multiprovider.providers.local import LocalModelProvider
from llm_multiprovider.providers.ollama import OllamaProvider
from llm_multiprovider.providers.openai import OpenAIProvider
from llm_multiprovider.providers.runpod_openai import RunpodOpenAIProvider
from llm_multiprovider.providers.runpod import RunpodProvider
from llm_multiprovider.providers.together_ai import TogetherAIProvider

class ModelProviderFactory:
    """Factory class to manage different model providers dynamically."""

    PROVIDERS: Dict[str, Type[ModelProviderBase]] = {
        "cerebras": CerebrasProvider,
        "groq": GroqProvider,
        "local": LocalModelProvider,
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,
        "runpod_openai": RunpodOpenAIProvider,
        "runpod": RunpodProvider,
        "together_ai": TogetherAIProvider,
    }

    @staticmethod
    def create_provider(provider_name: str, model_name: str, using_tokenizer: bool = False) -> ModelProviderBase:
        """
        Creates an instance of the specified model provider.

        Args:
            provider_name (str): Name of the provider (e.g., "cerebras", "openai", "ollama").
            model_name (str): Name of the model to use.

        Returns:
            ModelProviderBase: An instance of the selected provider.

        Raises:
            ValueError: If the provider is not recognized.
        """
        provider_name = provider_name.lower()
        if provider_name not in ModelProviderFactory.PROVIDERS:
            raise ValueError(f"❌ Unknown provider: {provider_name}. Available: {list(ModelProviderFactory.PROVIDERS.keys())}")

        provider_class = ModelProviderFactory.PROVIDERS[provider_name]

        # Pasa using_tokenizer solo si el provider lo soporta
        try:
            return provider_class(model_name, using_tokenizer=using_tokenizer)
        except TypeError:
            # El provider no acepta using_tokenizer, instáncialo “normal”
            return provider_class(model_name)



async def main():
    """Example usage of ModelProviderFactory."""
    
    provider_name = "ollama" #os.getenv("MODEL_PROVIDER", "openai")  # Por defecto usa OpenAI
    model_name = "qwen2.5:0.5b" #os.getenv("MODEL_NAME", "gpt-4-turbo")

    # Crear el proveedor dinámicamente
    provider = ModelProviderFactory.create_provider(provider_name, model_name)

    # Usar el proveedor para generar texto
    response = await provider.generate_text("Hello, how are you?", temperature=0.7)
    print(f"🔹 Response: {response}")

if __name__ == "__main__":
    asyncio.run(main())
