'''
# Prepare the payload for the RunPod endpoint
payload = {
        "generate": {
            "prompt": prompt,
            "max_new_tokens": 1,
            'return_full_text': True,
            #'num_return_sequences': 10, # doesnt work
            #'use_beam_search': True, # doesnt work
            'details': True,
            'return_full_text': True,
            'decoder_input_details': True,
            'top_n_tokens': 5,
            #'best_of': 2, # doesnt work
            #'do_sample': True,
            "seed": 51256138321                                                 
        },
        "sampling_params": {},   
    } 

payload = {
        "generate": {
            "prompt": prompt,  
            "max_new_tokens": 50,
            "top_k": 20, #20, #40,
            "top_p": 0.5,#0.8, #0.95,
            "temperature": 0.2, #0.6, #0.6, #0.9,
            "do_sample": True,
            "num_return_sequences": 3,
            "seed": 51256138321
        },
        "sampling_params": {"num_return_sequences": 3},   
    } 
'''
#Runpod https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_client
import asyncio
import os
import runpod
import torch
from llm_multiprovider.providers.base import ModelProviderBase
from typing import List, Dict, Any, Optional
from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper
from dotenv import load_dotenv
from llm_multiprovider.utils.metrics import *

# Load environment variables
load_dotenv()

class RunpodProvider(ModelProviderBase):
    """RunPod model provider."""

    def __init__(self, model_name: str, using_tokenizer:bool = False):
        super().__init__(model_name)
        self.api_key = os.getenv("RUNPOD_API_KEY")
        if not self.api_key:
            raise ValueError("RUNPOD_API_KEY is not set in the environment variables.")
        runpod.api_key = self.api_key

        if using_tokenizer:    
            self.tokenizer = TokenizerMapper.get_tokenizer(model_name)                
        self.endpoint = runpod.Endpoint(os.getenv("RUNPOD_ENDPOINT"))

    async def generate_text(self, prompt: str, **kwargs) -> List[str]:
        """Generates text using the RunPod endpoint."""
        self.logger.info(f"RunPod - Generating text for prompt: {prompt}")

        payload = {
            "generate": {
                "prompt": prompt,
                **kwargs
            },
            "sampling_params": {}, 
        }


        # Run the request through the endpoint
        print("payload", payload)
        response = await self._run_endpoint(payload)

        # Extract and return the generated text
        if response and 'generated_text' in response:
            return [response['generated_text']]
        else:
            self.logger.error("RunPod - No output received from the endpoint.")
            return []

    async def chat_completion(self, messages: List[Dict[str, Any]], **kwargs) -> List[str]:
        """Generates chat completion using the RunPod endpoint."""
        self.logger.info(f"RunPod - Generating chat completion for messages: {messages}")

        # Formatear los mensajes utilizando el chat template del tokenizer
        formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)

        payload = {
            "generate": {
                "prompt": formatted_prompt,
                **kwargs
            },
            "sampling_params": {},
        }

        
        # Llamar a RunPod para procesar la solicitud
        self.logger.info(f"RunPod - Sending payload: {payload}")
        response = await self._run_endpoint(payload)

        # Extraer y devolver el texto generado
        if response and 'generated_text' in response:
            generated_text = response['generated_text']
            if "<|begin_of_text|>" in generated_text:
                generated_text = generated_text.split("<|begin_of_text|>")[1]
            return [generated_text]
        else:
            self.logger.error("RunPod - No output received from the endpoint.")
            return []



    async def logprobs(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Retrieves log probabilities for the next token based on the given prompt."""
        self.logger.info(f"RunPod - Fetching logprobs for prompt: {prompt}")

        # Prepare the payload for the RunPod endpoint
        payload = {
                "generate": {
                    "prompt": prompt,
                    "max_new_tokens": 1,
                    'return_full_text': True,
                    #'num_return_sequences': 10, # doesnt work
                    #'use_beam_search': True, # doesnt work
                    'details': True,
                    'return_full_text': True,
                    'decoder_input_details': True,
                    'top_n_tokens': 5,
                    #'best_of': 2, # doesnt work
                    #'do_sample': True,
                    "seed": 51256138321                                                 
                },
                "sampling_params": {},   
            } 

        self.logger.info(f"RunPod - Sending payload: {payload}")
        # Run the request through the endpoint
        response = await self._run_endpoint(payload)

        self.logger.info(f"RunPod - Full response: {payload}")

        # Verifica si la respuesta tiene detalles
        if response and 'details' in response:
            details = response["details"]

            # Extraer tokens generados y sus logprobs
            if "tokens" in details:
                token_logprobs = [
                    {"token": token["text"], "logprob": token["logprob"]}
                    for token in details["tokens"]
                    if not token.get("special", False)  # Evitar tokens especiales como "<s>"
                ]

            # Extraer top_n_tokens si está presente
            top_n_logprobs = []
            if "top_tokens" in details:
                top_n_logprobs = [
                    [{"token": t["text"], "logprob": t["logprob"]} for t in top_n_list]
                    for top_n_list in details["top_tokens"]
                ]

            return {
                "token_logprobs": token_logprobs,
                "top_n_logprobs": top_n_logprobs
            }

        else:
            self.logger.error("RunPod - No logprobs received from the endpoint.")
            return None



    async def get_logprobs_for_target_output(self, prompt: str, target_output: str) -> Optional[Dict[str, Any]]:
        """Get log-probabilities for each token in the target output."""
        self.logger.info(f"RunPod - Fetching logprobs for prompt + target_output: '{prompt} {target_output}'")

        # Combine prompt and target_output
        full_text = f"{prompt} {target_output}"

        # Prepare the payload for the RunPod endpoint
        payload = {
            "generate": {
                "prompt": full_text,
                "max_new_tokens": 1,  # Solo se genera un token extra
                "return_full_text": True,
                "details": True,  # Necesario para obtener logprobs
                "decoder_input_details": True,
                "top_n_tokens": 5,
                "seed": 51256138321                                                 
            },
            "sampling_params": {},   
        } 

        self.logger.info(f"RunPod - Sending payload: {payload}")
        
        # Run the request through the endpoint
        response = await self._run_endpoint(payload)

        self.logger.info(f"RunPod - Full response: {response}")

        # Verifica si la respuesta tiene detalles
        if response and 'details' in response:
            details = response["details"]

            # Extraer `prefill` tokens (contienen el prompt y parte del target_output)
            if "prefill" in details:
                all_tokens = [t["text"] for t in details["prefill"] if not t.get("special", False)]
                all_logprobs = [t["logprob"] for t in details["prefill"] if not t.get("special", False)]
                all_token_ids = [t["id"] for t in details["prefill"] if not t.get("special", False)]
            else:
                self.logger.error("RunPod - No prefill data found in response.")
                return None

            # Determinar la cantidad de tokens en el prompt
            prompt_token_length = len(self.tokenizer.encode(prompt, add_special_tokens=False))

            # Extraer solo los tokens de target_output
            target_tokens = all_tokens[prompt_token_length:]
            target_logprobs = all_logprobs[prompt_token_length:]
            target_token_ids = all_token_ids[prompt_token_length:]

            # Reconstruir el texto de target_output
            target_text = self.tokenizer.decode(target_token_ids)

            # Extraer `top_n` logprobs si están presentes
            top_n_logprobs = []
            if "top_tokens" in details:
                top_n_logprobs = [
                    [{"token": t["text"], "logprob": t["logprob"]} for t in top_n_list]
                    for top_n_list in details["top_tokens"][prompt_token_length:]
                ]

            return {
                "tokens": target_tokens,
                "token_logprobs": target_logprobs,
                "token_ids": target_token_ids,
                "reconstructed_text": target_text,
                "top_n_logprobs": top_n_logprobs
            }

        else:
            self.logger.error("RunPod - No logprobs received from the endpoint.")
            return None



    async def _run_endpoint(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Helper function to run the endpoint and handle responses."""
        try:
            # Run the request through the endpoint
            job = self.endpoint.run(payload)

            # Poll the job status
            while True:
                await asyncio.sleep(0.5)
                status = job.status()
                print("status", status)
                if status == "COMPLETED":
                    print("job", job)
                    theoutput = job.output() 
                    print("theoutput", theoutput)
                    return theoutput
                elif status in ["CANCELLED"]:
                    self.logger.error("RunPod - Job cancelled by user.")
                    return None
                elif status in ["FAILED"]:
                    self.logger.error("RunPod - Job failed or encountered an error.")
                    return None
        except Exception as e:
            self.logger.error(f"RunPod - Error running endpoint: {e}")
            return None





async def main():
    """Main function to test TogetherAIProvider."""
    model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"
    provider = RunpodProvider(model_name)
    
    print("\n🔹 Testing generate_text...")
    response = await provider.generate_text("Hello, how are you?", temperature=0.7, num_return_sequences=1, seed=51256138321, max_new_tokens = 50)
    print(f"🔹 Respuesta: {response}")
    
    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion(
        [{"role": "user", "content": "Tell me a joke"}], temperature=0.7, num_return_sequences=1, seed=51256138321, max_new_tokens = 50
    )
    print(f"🔹 Respuesta: {chat_response}")

    
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
    
if __name__ == "__main__":
    asyncio.run(main())