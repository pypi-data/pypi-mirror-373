#https://huggingface.co/docs/transformers/en/main_classes/text_generation
import os
import torch
import psutil
import asyncio
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from llm_multiprovider.providers.base import ModelProviderBase
from llm_multiprovider.utils.tokenizer_mapper import TokenizerMapper
from llm_multiprovider.utils.metrics import *
'''
def calculate_perplexity(logits, target):
    """
    Calculate perplexity from logits and target labels.

    Args:
    - logits (torch.Tensor): Logits output from the model (batch_size, seq_length, vocab_size).
    - target (torch.Tensor): Ground truth labels (batch_size, seq_length).

    Returns:
    - perplexity (float): The perplexity score.
    """

    # Convert logits to log probabilities
    log_probs = torch.nn.functional.log_softmax(logits, dim=-1)

    # Gather the log probabilities for the correct target tokens
    # log_probs has shape (batch_size, seq_length, vocab_size)
    # target has shape (batch_size, seq_length)
    # The gather method will pick the log probabilities of the true target tokens
    target = torch.tensor(target, dtype=torch.long)
    target_log_probs = log_probs.gather(dim=-1, index=target.unsqueeze(-1)).squeeze(-1)
    print("log_probs",log_probs)
    print("target",target)    
    print("target_log_probs",target_log_probs)    

    # Calculate the negative log likelihood
    negative_log_likelihood = -target_log_probs

    # Calculate the mean negative log likelihood over all tokens
    mean_nll = negative_log_likelihood.mean()

    # Calculate perplexity as exp(mean negative log likelihood)
    perplexity = torch.exp(mean_nll)

    return perplexity.item()
'''

class LocalModelProvider(ModelProviderBase):
    """Local model provider with quantization support."""

    def __init__(self, model_name: str, quantize: bool = True):
        super().__init__(model_name)
        self.quantize = quantize
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load tokenizer using TokenizerMapper
        self.tokenizer = TokenizerMapper.get_tokenizer(model_name)

        # Load the model with optional quantization
        self.model = self._load_model(model_name)

        # Log actual memory usage after loading the model
        self._log_memory_usage()

    def _load_model(self, model_name: str):
        """Load the model with or without quantization."""
        self.logger.info(f"Loading local model '{model_name}' with quantization={self.quantize}...")

        if self.quantize:
            self.logger.info("Applying 4-bit quantization using bitsandbytes...")
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type='nf4',
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                memory_efficient_fp32_offload=True
            )
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                quantization_config=quant_config
            ).to(self.device)
        else:
            self.logger.info("Loading model without quantization...")
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True
            ).to(self.device)

        return model

    def _log_memory_usage(self):
        """Log the system's memory usage."""
        memory_info = psutil.virtual_memory()
        total_memory_used = memory_info.total - memory_info.available
        total_memory_used_gb = total_memory_used / (1024 ** 3)
        self.logger.info(f"Actual memory usage after loading model: {total_memory_used_gb:.2f} GB")

    async def generate_text(self, prompt: str, **kwargs) -> list:
        """Genera múltiples textos utilizando el modelo local."""
        self.logger.info(f"Modelo local - Generando texto para el prompt: {prompt}")

        seed = kwargs.pop("seed", None)
        if seed is not None:
            torch.manual_seed(seed)
            self.logger.info(f"Semilla de torch establecida en {seed}")

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        attention_mask = torch.ones(input_ids.shape, device=self.device)

        # Establece do_sample=True para permitir la generación de muestras
        #kwargs["do_sample"] = kwargs.get("do_sample", True)
        # Asegúrate de que num_return_sequences esté definido
        num_return_sequences = kwargs.get("num_return_sequences", 1)

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                **kwargs
            )

        # Decodifica todas las secuencias generadas y elimina el prompt del resultado
        responses = []
        for i in range(num_return_sequences):
            response = self.tokenizer.decode(generated_ids[i], skip_special_tokens=True)
            print("full response", response)
            # Elimina el prompt del inicio de la respuesta, si está presente
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            responses.append(response)

        self.logger.info(f"Respuestas generadas: {responses}")
        return responses

    async def chat_completion(self, messages: list, **kwargs) -> list:
        """Genera múltiples respuestas para una conversación utilizando el modelo local."""
        print("messages", messages)
        
        # Aplica la plantilla de chat y tokeniza
        formatted_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False)
        print("formatted_prompt", formatted_prompt)
        input_ids = self.tokenizer.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
        )
        
        # Mueve los tensores al dispositivo adecuado
        input_ids = input_ids.to(self.device)
        attention_mask = torch.ones(input_ids.shape, device=self.device)
        print("tokenized_chat", input_ids)
        print("self.tokenizer.decode(tokenized_chat[0])", self.tokenizer.decode(input_ids[0]))

        num_return_sequences = kwargs.get("num_return_sequences", 1)

        with torch.no_grad():
            generated_ids = self.model.generate(
                input_ids,
                attention_mask=attention_mask,
                **kwargs
            )

        # Decodifica todas las secuencias generadas y elimina el prompt del resultado
        responses = []
        for i in range(num_return_sequences):
            response = self.tokenizer.decode(generated_ids[i], skip_special_tokens=True)
            self.logger.info(f"Full generated response: {response}")

            # Elimina el prompt del inicio de la respuesta, si está presente
            formatted_prompt = self.tokenizer.decode(input_ids[0], skip_special_tokens=True)
            if response.startswith(formatted_prompt):
                response = response[len(formatted_prompt):].strip()
            responses.append(response)

        self.logger.info(f"Generated responses: {responses}")
        return responses

    async def logprobs(self, prompt: str, **kwargs):
        """Retrieves log probabilities for the next token based on the given prompt."""
        self.logger.info(f"Local model - Fetching logprobs for prompt: {prompt}")
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids)
            logits = outputs.logits

        last_token_logits = logits[0, -1, :]
        probabilities = torch.softmax(last_token_logits, dim=-1)
        top_probs, top_indices = torch.topk(probabilities, 10)
        tokens = self.tokenizer.convert_ids_to_tokens(top_indices.tolist())

        return {token: prob.item() for token, prob in zip(tokens, top_probs)}

    async def get_logprobs_for_target_output(self, prompt: str, target_output: str):
        """Get log-probabilities for each token in the target output."""
        self.logger.info(f"Local model - Fetching logprobs for prompt + target_output: '{prompt} {target_output}'")

        input_text = prompt + " " + target_output
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt").to(self.device)
        prompt_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
        output_ids = input_ids[:, len(prompt_ids[0]):][0].tolist()

        with torch.no_grad():
            outputs = self.model(input_ids)
            logits = outputs.logits[0, len(prompt_ids[0]) - 1: len(input_ids[0]) - 1, :].cpu()

        #print("perplexity", calculate_perplexity(logits,output_ids))


        return self._get_logprobs_from_logits(logits, output_ids)

    def _get_logprobs_from_logits(self, logits, output_ids):
        """Calculate log probabilities from logits."""
        log_probs = torch.log_softmax(logits, dim=-1)
        selected_log_probs = log_probs[range(len(output_ids)), output_ids]
        tokens = self.tokenizer.convert_ids_to_tokens(output_ids)
        return {
            "tokens": tokens,
            "token_logprobs": selected_log_probs.tolist(),
            "token_ids": output_ids,
            "reconstructed_text": self.tokenizer.decode(output_ids)
        }





async def main():
    """Main function to test TogetherAIProvider."""
    model_name = "TensorML/fanslove_creator_70B_AWQ" #"Qwen/Qwen2.5-0.5B-Instruct"
    provider = LocalModelProvider(model_name)

    print("\n🔹 Testing generate_text...")
    response = await provider.generate_text("Hello, how are you?", temperature=0.7, num_return_sequences=2)
    print(f"🔹 Respuesta: {response}")
    
    print("\n🔹 Testing chat_completion...")
    chat_response = await provider.chat_completion(
        [{"role": "user", "content": "Tell me a joke"}], temperature=0.7, num_return_sequences=2
    )
    print(f"🔹 Respuesta: {chat_response}")

    print("\n🔹 Testing logprobs...")
    logprobs_response = await provider.logprobs("The capital of USA is ")
    print(f"🔹 Logprobs response: {logprobs_response}")

    
    
    print("\n🔹 Testing logprobs for target output...")
    prompt = "What is the capital of USA?"
    target_output = "The capital of USA is Washington D.C."    

    model_output = await provider.generate_text(prompt, do_sample=False, num_beams=1, num_return_sequences=1, max_new_tokens = 20)
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