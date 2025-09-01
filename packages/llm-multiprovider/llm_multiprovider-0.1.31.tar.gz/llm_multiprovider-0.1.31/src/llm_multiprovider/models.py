from llm_multiprovider.providers.openai import OpenAIProvider
from llm_multiprovider.providers.ollama import OllamaProvider
from llm_multiprovider.providers.together_ai import TogetherAIProvider
import logging

# Configure logging to show real-time logs
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ModelProviderFactory:
    _provider = None  # Store initialized provider

    @classmethod
    def initialize(cls, provider_type: str, model_name: str):
        """Initialize the provider once."""
        providers = {
            "openai": OpenAIProvider,
            "ollama": OllamaProvider,
            "together_ai": TogetherAIProvider,
        }
        if provider_type not in providers:
            raise ValueError(f"Unknown provider: {provider_type}")

        cls._provider = providers[provider_type](model_name)
        logger.info("Initialized ModelProviderFactory." + str(cls._provider))

    @classmethod
    def get_provider(cls):
        """Return the initialized provider."""
        if cls._provider is None:
            raise ValueError("ModelProviderFactory is not initialized. Call initialize() first.")
        return cls._provider

