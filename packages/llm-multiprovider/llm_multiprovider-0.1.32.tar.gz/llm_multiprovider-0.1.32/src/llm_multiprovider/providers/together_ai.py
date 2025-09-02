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

class TogetherAIProvider(ModelProviderBase):
    """TogetherAI model provider."""

    def __init__(self, model_name: str, using_tokenizer:bool = False):
        super().__init__(model_name)
        self.api_key = os.getenv("TOGETHER_API_KEY")
        self.base_url = os.getenv("TOGETHER_BASE_URL", "https://api.together.xyz/v1/chat/completions")

        if not self.api_key:
            raise ValueError("TOGETHER_API_KEY is not set in the .env file.")

        # Load tokenizer using TokenizerMapper
        if using_tokenizer:           
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name)

        self.client = AsyncClient(api_key=self.api_key, base_url=self.base_url)

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generates text from TogetherAI."""
        self.logger.info(f"TogetherAI - Generating text for prompt: {prompt}")

        response = await self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            **kwargs
        )

        all_texts = []
        for choice in response.choices:
            all_texts.append(choice.text)

        return all_texts
    
    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> str:
        """Handles chat-based conversation with TogetherAI."""
        self.logger.info(f"TogetherAI - Handling chat: {messages}")

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            **kwargs
        )
        print("response", response)
        all_texts = []
        for choice in response.choices:
            all_texts.append(choice.message.content)

        return all_texts

    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Retrieves log probabilities for the next token based on the given prompt."""
        self.logger.info(f"TogetherAI - Fetching logprobs for prompt: {prompt}")

        response = await self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            max_tokens= 1,
            logprobs=1,  # Request log probabilities for tokens
            **kwargs
        )

        return response



    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """
        Get log-probabilities for each token in the target output.

        Args:
            prompt (str): The input prompt.
            target_output (str): The expected output sequence.

        Returns:
            dict: A dictionary containing log probabilities for only the target_output tokens.
        """
        self.logger.info(f"TogetherAI - Fetching logprobs for prompt + target_output: '{prompt} {target_output}'")

        # Tokenize prompt and target_output
        full_text = f"{prompt} {target_output}"
        full_token_ids = self.tokenizer.encode(full_text, add_special_tokens=False)
        prompt_token_ids = self.tokenizer.encode(prompt, add_special_tokens=False)

        prompt_token_length = len(prompt_token_ids)  # Length of the prompt in tokens

        try:
            response = await self.client.completions.create(
                model=self.model_name,
                prompt=full_text,
                echo=True,  # Ensures logprobs are returned for the entire sequence
                logprobs=1,  # Get log probabilities for each token
                max_tokens= 1,
            )
            print("🔍 Full API Response:", response)  # Debugging full API response

            print("response.prompt[0]", response.prompt[0])

            logprobs_data = response.prompt[0]["logprobs"]  # Corrected access path

            tokens = logprobs_data["tokens"]
            token_logprobs = logprobs_data["token_logprobs"]
            token_ids = logprobs_data["token_ids"]

            # Extract only logprobs for target_output tokens
            target_tokens = tokens[prompt_token_length:]  
            target_logprobs = token_logprobs[prompt_token_length:]  
            target_token_ids = token_ids[prompt_token_length:]  

            # 🔍 DEBUG: Convert target_tokens back to text and check correctness
            target_text = self.tokenizer.convert_tokens_to_string(target_tokens)
            print("✅ Reconstructed Target Output:", target_text)
            print("🔹 Target Tokens:", target_tokens)
            print("🔹 Target Logprobs:", target_logprobs)            
            print("🔹 Target Token IDs:", target_token_ids)                        

            return {
                "tokens": target_tokens,
                "token_logprobs": target_logprobs,
                "token_ids": target_token_ids,
                "reconstructed_text": target_text
            }

        except Exception as e:
            error_trace = traceback.format_exc()
            self.logger.error(f"❌ TogetherAI logprobs error: {e}\n{error_trace}")
            return None







async def main():
    """Main function to test TogetherAIProvider."""
    model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    provider = TogetherAIProvider(model_name)

    print("\n🔹 Testing generate_text...")
    response = await provider.generate_text("Hello, how are you?", temperature=0.7, n=1)
    print(f"🔹 Respuesta: {response}")
    
    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion(
        [{"role": "user", "content": "Tell me a joke"}], temperature=0.7
    )
    print(f"🔹 Respuesta: {chat_response}")
    
    print("\n🔹 Testing logprobs...")
    logprobs_response = await provider.logprobs("The capital of USA is ")
    print(f"🔹 Logprobs response: {logprobs_response}")

    
    
    print("\n🔹 Testing logprobs for target output...")
    prompt = "What is the capital of USA?"
    target_output = "The capital of USA is Washington D.C."    

    model_output = await provider.generate_text(prompt, temperature=0, n=1, max_tokens = 20)
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
if __name__ == "__main__":
    asyncio.run(main())