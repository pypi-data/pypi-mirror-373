import asyncio
import os
import httpx
import logging
from llm_multiprovider.providers.base import ModelProviderBase
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GroqProvider(ModelProviderBase):
    """Groq model provider."""

    def __init__(self, model_name: str, using_tokenizer:bool = False):
        """
        Initializes the provider for the Groq model.

        Args:
            model_name (str): Name of the model in Groq (e.g., "llama-3.3-70b-versatile").
        """
        super().__init__(model_name)
        self.base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        self.api_key = os.getenv("GROQ_API_KEY")
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

        # Load tokenizer using TokenizerMapper
        if using_tokenizer:
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name)

    async def send_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Helper function to send requests and log responses.

        Args:
            endpoint (str): API endpoint to send the request to.
            payload (Dict[str, Any]): JSON payload to send in the request.

        Returns:
            Optional[Dict[str, Any]]: Parsed JSON response from the API.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}{endpoint}", json=payload, headers=self.headers)
        
        logger.debug(f"📡 Sent request to: {self.base_url}{endpoint}")
        logger.debug(f"📨 Request payload: {payload}")
        logger.debug(f"🔄 Response status: {response.status_code}")
        logger.debug(f"🔎 Response headers: {response.headers}")
        logger.debug(f"📜 Response raw text: {response.text}")

        response.raise_for_status()  # Ensure we catch HTTP errors early

        response_data = response.json()
        logger.debug(f"📦 Parsed JSON response: {response_data}")

        return response_data

    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        """
        Generates text using the Groq model.

        Args:
            prompt (str): The input prompt for text generation.
            kwargs (dict): Additional parameters like temperature and max_tokens.

        Returns:
            List[str]: Generated text responses.
        """
        logger.info(f"Groq - Generating text for prompt: {prompt}")

        request_payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            **kwargs
        }

        response_data = await self.send_request("/chat/completions", request_payload)
        return [choice["message"]["content"] for choice in response_data.get("choices", [])]

    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        """
        Handles chat-based conversation with the Groq model.

        Args:
            messages (List[Dict[str, Any]]): List of messages in JSON format representing the conversation history.
            kwargs (dict): Additional parameters like temperature and max_tokens.

        Returns:
            List[str]: Generated chat responses.
        """
        logger.info(f"Groq - Handling chat: {messages}")

        request_payload = {
            "model": self.model_name,
            "messages": messages,
            **kwargs
        }

        response_data = await self.send_request("/chat/completions", request_payload)
        return [choice["message"]["content"] for choice in response_data.get("choices", [])]

    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Not implemented: Method to obtain log-probabilities for the next tokens based on the input.

        Args:
            prompt (str): The input prompt for text generation.
            kwargs (dict): Additional parameters.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError("The 'logprobs' method is not implemented for GroqProvider.")

    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """
        Not implemented: Method to obtain log-probabilities for each token in the expected output.

        Args:
            prompt (str): The input prompt for text generation.
            target_output (str): The expected output text.

        Raises:
            NotImplementedError: This method is not implemented.
        """
        raise NotImplementedError("The 'get_logprobs_for_target_output' method is not implemented for GroqProvider.")

# Example usage
async def main():
    """Main function to test GroqProvider."""
    model_name = "llama-3.3-70b-versatile"  # Model in Groq
    provider = GroqProvider(model_name)
    
    print("\n🔹 Testing generate_text...")
    response = await provider.generate_text("Hello, how are you?", temperature=0.7)
    print(f"🔹 Response: {response}")
    
    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion(
        [{"role": "user", "content": "Tell me a joke"}], temperature=0.7
    )
    print(f"🔹 Chat Response: {chat_response}")

if __name__ == "__main__":
    asyncio.run(main())
