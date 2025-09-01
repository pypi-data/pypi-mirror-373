import asyncio
import os
import traceback
from openai import AsyncClient
from llm_multiprovider.providers.base import ModelProviderBase
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import math
from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper
from llm_multiprovider.utils.metrics import *

# Load environment variables
load_dotenv()

class OpenAIProvider(ModelProviderBase):
    """OpenAI model provider."""


    def __init__(self, model_name: str, using_tokenizer:bool = False):
        super().__init__(model_name)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in the .env file.")

        # Load tokenizer using TokenizerMapper
        if using_tokenizer:           
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name)

        self.client = AsyncClient(api_key=self.api_key, base_url=self.base_url)

    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        raise Exception("Not Implemented")

    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        """Handles chat-based conversation with OpenAI."""
        self.logger.info(f"OpenAI - Handling chat: {messages}")

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            **kwargs
        )

        return [choice.message.content for choice in response.choices]

    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        raise Exception("Not Implemented")


    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        raise Exception("Not Implemented")


async def main():
    """Main function to test OpenAIProvider."""
    model_name = "gpt-4o"  # Modelo gratuito de OpenAI
    provider = OpenAIProvider(model_name)

    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion(
        [{"role": "user", "content": "Tell me a joke"}], temperature=0.7
    )
    print(f"🔹 Respuesta: {chat_response}")

if __name__ == "__main__":
    asyncio.run(main())
