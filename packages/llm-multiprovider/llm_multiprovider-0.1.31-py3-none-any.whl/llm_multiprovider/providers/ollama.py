#OLLAMA REST API https://www.postman.com/postman-student-programs/ollama-api/request/uprcxdn/chat-completion-with-tools

import asyncio
import os
import traceback
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

class OllamaProvider(ModelProviderBase):
    """Ollama model provider."""

    def __init__(self, model_name: str, using_tokenizer:bool = False):
        super().__init__(model_name)
        self.base_url = os.getenv("OLLAMA_BASE_URL")  # Ollama corre localmente por defecto

        # Load tokenizer using TokenizerMapper
        if using_tokenizer:        
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name)

    async def send_request(self, payload: Dict[str, Any], base_url:str) -> Optional[Dict[str, Any]]:
        """Helper function to send requests and log responses."""
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(base_url, json=payload)
        
        logger.debug(f"📡 Sent request to: {base_url}")
        logger.debug(f"📨 Request payload: {payload}")
        logger.debug(f"🔄 Response status: {response.status_code}")
        logger.debug(f"🔎 Response headers: {response.headers}")
        logger.debug(f"📜 Response raw text: {response.text}")

        response.raise_for_status()  # Ensure we catch HTTP errors early

        response_data = response.json()
        logger.debug(f"📦 Parsed JSON response: {response_data}")

        return response_data

    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        """Generates text from Ollama."""
        logger.info(f"Ollama - Generating text for prompt: {prompt}")

        request_payload = {
            "model": self.model_name,
            "prompt": prompt,
            "options": kwargs,  # 👈 kwargs dentro de 'options'
            "stream": False
        }

        response_data = await self.send_request(request_payload, self.base_url + "/generate")
        return [response_data["response"]] if response_data and "response" in response_data else []

    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        """Handles chat-based conversation with Ollama."""
        logger.info(f"Ollama - Handling chat: {messages}")

        request_payload = {
            "model": self.model_name,
            "messages": messages,
            "options": kwargs,  # 👈 kwargs dentro de 'options'
            "stream": False
        }

        response_data = await self.send_request(request_payload, self.base_url + "/chat")
        return [response_data["response"]] if response_data and "response" in response_data else []

    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        raise Exception("Not Implemented")

    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        raise Exception("Not Implemented")

async def main():

    """Main function to test OllamaProvider."""
    model_name = "g1ibby/miqu:70b"#"qwen2.5:0.5b" #"qwen2.5:0.5b"  # Modelo en Ollama
    provider = OllamaProvider(model_name)
    
    
    print("\n🔹 Testing generate_text...")
    response = await provider.generate_text("Hello, how are you?", temperature=0.7)
    print(f"🔹 Response: {response}")
    
    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion(
        [{"role": "user", "content": "Tell me a joke"}], temperature=0.7
    )
    print(f"🔹 Chat Response: {response}")
    '''
    payload = {
      "model": model_name,
      "messages": [
        {
          "role": "user",
          "content": "What is the weather today in Paris?"
        }
      ],
      "stream": False,
      "tools": [
        {
          "type": "function",
          "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a location",
            "parameters": {
              "type": "object",
              "properties": {
                "location": {
                  "type": "string",
                  "description": "The location to get the weather for, e.g. San Francisco, CA"
                },
                "format": {
                  "type": "string",
                  "description": "The format to return the weather in, e.g. 'celsius' or 'fahrenheit'",
                  "enum": ["celsius", "fahrenheit"]
                }
              },
              "required": ["location", "format"]
            }
          }
        }
      ]
    }
    '''
 
 
 
if __name__ == "__main__":
    asyncio.run(main())
