#TODO --> Not finished. Work in Progress.
import asyncio
import os
import requests
import json
from llm_multiprovider.providers.base import ModelProviderBase
from typing import List, Dict, Any, Optional
from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper
from dotenv import load_dotenv
from llm_multiprovider.utils.metrics import *

# Load environment variables
load_dotenv()

class RunpodOpenAIProvider(ModelProviderBase):
    """RunPod model provider using OpenAI-style API."""

    def __init__(self, model_name: str, using_tokenizer:bool = False):
        super().__init__(model_name)
        self.api_key = os.getenv("RUNPOD_OPENAI_API_KEY")
        self.endpoint = os.getenv("RUNPOD_OPENAI_ENDPOINT")
        self.secret_key = os.getenv("RUNPOD_X_SECRET_KEY")

        print("self.endpoint", self.endpoint)
        
        if not self.api_key:
            raise ValueError("RUNPOD_API_KEY is not set in the environment variables.")
        if using_tokenizer:    
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name)

    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        """Generates text using the RunPod OpenAI-style endpoint."""
        self.logger.info(f"RunPod OpenAI - Generating text for prompt: {prompt}")

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": kwargs.get("max_new_tokens", 100),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "n": kwargs.get("num_return_sequences", 1),
        }

        payload = {       
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": 1000,
                "top_k": 20, #50,#20,
                "top_p": 0.5,
                "temperature": 0.2, #0.6, #0.5,#0.2
                }  

        response = await self._post_request(payload)

        return [choice["text"] for choice in response["choices"]] if response and "choices" in response else []

    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        """Generates chat completion using the RunPod OpenAI-style endpoint."""
        self.logger.info(f"RunPod OpenAI - Generating chat completion for messages: {messages}")

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": kwargs.get("max_new_tokens", 100),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "n": kwargs.get("num_return_sequences", 1),
        }

        response = await self._post_request(payload)

        return [choice["message"]["content"] for choice in response["choices"]] if response and "choices" in response else []

    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Retrieves log probabilities for the next token based on the given prompt."""
        self.logger.info(f"RunPod OpenAI - Fetching logprobs for prompt: {prompt}")

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": 1,
            "logprobs": 5,
            "echo": True,
        }

        response = await self._post_request(payload)
        return self._extract_logprobs(response) if response else None

    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """Get log-probabilities for each token in the target output."""
        self.logger.info(f"RunPod OpenAI - Fetching logprobs for prompt + target_output: '{prompt} {target_output}'")

        payload = {
            "model": self.model_name,
            "prompt": f"{prompt} {target_output}",
            "max_tokens": 1,
            "logprobs": 5,
            "echo": True,
        }

        response = await self._post_request(payload)
        return self._extract_logprobs(response, prompt) if response else None

    async def _post_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper function to send a POST request to the RunPod OpenAI API."""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.api_key 
            }            
            print("headers", headers)
            print("payload", payload)
            response = requests.post(self.endpoint, json=payload, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"RunPod OpenAI - API request failed with status {response.status_code}: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"RunPod OpenAI - Error making POST request: {e}")
            return None

    def _extract_logprobs(self, response: Dict[str, Any], prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Extracts log probabilities from the OpenAI-style response."""
        if "choices" not in response:
            return None

        logprobs_data = response["choices"][0].get("logprobs", {})
        all_tokens = logprobs_data.get("tokens", [])
        all_logprobs = logprobs_data.get("token_logprobs", [])
        top_logprobs = logprobs_data.get("top_logprobs", [])

        if prompt:
            prompt_token_length = len(self.tokenizer.encode(prompt, add_special_tokens=False))
            target_tokens = all_tokens[prompt_token_length:]
            target_logprobs = all_logprobs[prompt_token_length:]
            return {
                "tokens": target_tokens,
                "token_logprobs": target_logprobs,
                "top_n_logprobs": top_logprobs[prompt_token_length:],
            }

        return {
            "tokens": all_tokens,
            "token_logprobs": all_logprobs,
            "top_n_logprobs": top_logprobs,
        }


async def main():
    model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    provider = RunpodOpenAIProvider(model_name)

    print("\n🔹 Testing generate_text...")
    response = await provider.generate_text("Hello, how are you?")
    print(f"🔹 Response: {response}")
    '''
    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion([{"role": "user", "content": "Tell me a joke"}])
    print(f"🔹 Response: {chat_response}")

    print("\n🔹 Testing logprobs...")
    logprobs_response = await provider.logprobs("The capital of USA is ")
    print(f"🔹 Logprobs response: {logprobs_response}")


    print("\n🔹 Testing logprobs for target output...")
    prompt = "What is the capital of USA?"
    target_output = "The capital of USA is Washington D.C."    

    #No funciona con temperatura 0.1
    model_output = await provider.generate_text(prompt, temperature=0.1, num_return_sequences=1, seed=51256138321, max_new_tokens = 20)
    print("model_output", model_output)
    model_output = model_output[0]
    print("model_output", model_output)


    logprobs_response = await provider.get_logprobs_for_target_output(prompt, target_output)
    
    if logprobs_response:
        print("\n🔍 Logprobs Details:")
        print(f"Reconstructed target text: {logprobs_response.get('reconstructed_text')}")
        print(f"Tokens: {logprobs_response.get('tokens')}")
        print(f"Token IDs: {logprobs_response.get('token_ids')}")
        print(f"Token log probabilities: {logprobs_response.get('token_logprobs')}")
    else:
        print("❌ Failed to fetch logprobs for target output.")

    metrics_to_calculate = ["log_probability", "perplexity", "meteor_score", "cosine_similarity"]
    metrics = calculate_metrics_from_logprobs(logprobs_response.get('token_logprobs'), metrics_to_calculate, target_output, model_output, model_type="all-mpnet-base-v2", debug=True)
    print("metrics", metrics)
    '''

if __name__ == "__main__":    
    asyncio.run(main())
