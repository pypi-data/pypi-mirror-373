import asyncio
import os
from llm_multiprovider.models import ModelProviderFactory
import uvicorn
import logging

# Configure logging to show real-time logs
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def main():
    provider_type = "together_ai"
    model_name = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    logger.info("Initializing ModelProviderFactory.")
    ModelProviderFactory.initialize(provider_type, model_name)
    logger.info("Starting FastAPI server with TogetherAI provider.")

    uvicorn.run("llm_multiprovider.api:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")

if __name__ == "__main__":
    asyncio.run(main())

