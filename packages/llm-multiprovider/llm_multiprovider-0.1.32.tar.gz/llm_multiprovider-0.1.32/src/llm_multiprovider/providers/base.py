import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ModelProviderBase(ABC):
    """Abstract base class for all model providers."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        """Generate text from the model and return all responses as a list of strings."""
        pass

    @abstractmethod
    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        """Generate chat completions and return all responses as a list of strings."""
        pass

    @abstractmethod
    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get log probabilities if supported; otherwise, return None."""
        pass

    @abstractmethod
    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """
        Get log-probabilities for each token in the target output.

        Args:
            prompt (str): The input prompt.
            target_output (str): The expected output sequence.

        Returns:
            dict: A dictionary containing log probabilities for only the target_output tokens.
        """
        pass
