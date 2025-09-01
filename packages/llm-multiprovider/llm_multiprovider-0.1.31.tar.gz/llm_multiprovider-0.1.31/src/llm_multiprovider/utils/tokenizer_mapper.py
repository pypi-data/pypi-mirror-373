import os
import logging
import traceback
from transformers import AutoTokenizer
import tiktoken

class TokenizerMapper:
    """
    Class to map model names to their respective tokenizers.
    If the model has no mapping, it attempts to use the model name directly.
    """

    MODEL_TOKENIZER_MAP = {
        # Meta LLaMA Models
        "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free": "meta-llama/Llama-3.3-70B-Instruct",
        "llama3.3:70b": "meta-llama/Llama-3.3-70B-Instruct",
        "llama-3.3-70b": "meta-llama/Llama-3.3-70B-Instruct",
        "llama-3.3-70b-versatile": "meta-llama/Llama-3.3-70B-Instruct",

        # DeepSeek Models
        "deepseek-r1:1.5b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "deepseek-r1:7b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "deepseek-r1:8b": "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
        "deepseek-r1:14b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "deepseek-r1:32b": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        "deepseek-r1:70b": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "deepseek-r1:671b": "deepseek-ai/DeepSeek-R1",
        "deepseek-coder:33b": "meta-llama/Meta-Llama-3.1-33B",

        # Other Transformers Models
        "meta-llama/Llama-3.1-8B-Instruct-Turbo": "meta-llama/Llama-3.1-8B",
        "mistral:7b": "mistralai/Mistral-7B-v0.1",
        "phi-2": "microsoft/phi-2",

        "qwen2.5:0.5b": "Qwen/Qwen2.5-72B-Instruct",
        "qwen2.5:7b": "Qwen/Qwen2.5-72B-Instruct",        
        "Qwen/Qwen2.5-0.5B-Instruct": "Qwen/Qwen2.5-0.5B-Instruct",
        "qwen2.5-custom:latest": "Qwen/Qwen2.5-0.5B",

        "mistral": "mistralai/Mistral-7B-Instruct-v0.3",
        "g1ibby/miqu:70b": "mistralai/Mistral-7B-Instruct-v0.3",
        "alpindale/miqu-1-70b-pytorch": "mistralai/Mistral-7B-Instruct-v0.3",
        "TensorML/fanslove_creator_70B_AWQ": "mistralai/Mistral-7B-Instruct-v0.3"
    }

    OPENAI_MODELS = {"gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o"}

    @staticmethod
    def get_tokenizer(model_name: str):
        """Retrieves the corresponding tokenizer for a model."""

        logging.info(f"🔍 Looking for tokenizer of model '{model_name}'")

        # ✅ Case 1: OpenAI Models (Use tiktoken)
        if model_name in TokenizerMapper.OPENAI_MODELS:
            logging.info(f"🟢 Using tiktoken tokenizer for OpenAI model '{model_name}'")
            try:
                return tiktoken.encoding_for_model(model_name)
            except KeyError:
                logging.warning(f"⚠️ No specific tokenizer found for {model_name}, using cl100k_base as fallback.")
                return tiktoken.get_encoding("cl100k_base")

        # ✅ Case 2: Transformers-based models (Use AutoTokenizer)
        tokenizer_name = TokenizerMapper.MODEL_TOKENIZER_MAP.get(model_name, model_name)
        huggingface_token = os.getenv("HUGGINGFACE_TOKEN")

        try:
            logging.info(f"🔍 Loading tokenizer for model '{model_name}': {tokenizer_name}")
            tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, token=huggingface_token, trust_remote_code=True)
            logging.info(f"✅ Successfully loaded tokenizer '{tokenizer_name}' for model '{model_name}'")
            return tokenizer
        except Exception as e:
            error_trace = traceback.format_exc()
            logging.error(
                f"❌ Error loading tokenizer '{tokenizer_name}' for model '{model_name}'.\n"
                f"Details: {e}\n{error_trace}"
            )
            raise RuntimeError(f"Could not load tokenizer for model: {model_name}")