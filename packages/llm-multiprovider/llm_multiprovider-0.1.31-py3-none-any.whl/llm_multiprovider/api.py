from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Extra
from llm_multiprovider.models import ModelProviderFactory
from typing import Optional, Dict, Any
import logging

# Force logging to always display messages
logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

app = FastAPI(title="My LLM API")

class GenerateRequest(BaseModel):
    prompt: str
    kwargs: Dict[str, Any] = {}

    class Config:
        extra = Extra.allow

class ChatRequest(BaseModel):
    messages: list

class LogProbsRequest(BaseModel):
    prompt: str

@app.on_event("startup")
async def startup_event():
    """Initialize ModelProviderFactory when FastAPI starts."""
    logger.debug("🔥 Initializing ModelProviderFactory...")
    ModelProviderFactory.initialize(provider_type="together_ai", model_name="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free")

@app.post("/generate")
async def generate(request: GenerateRequest):
    """Handles text generation using the configured provider."""
    logger.debug("🚀 generate")
    provider = ModelProviderFactory.get_provider()

    # Merge extra parameters with explicit kwargs
    kwargs = {**request.dict(exclude={"prompt", "kwargs"}), **request.kwargs}  

    try:
        result = await provider.generate_text(request.prompt, **kwargs)
        if result is None:
            raise HTTPException(status_code=500, detail="Provider returned None")
        return {"response": result}  # ✅ Return only the text
    except Exception as e:
        logger.error(f"❌ Exception in /generate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/chat")
async def chat(request: ChatRequest):
    """Handles chat completion using the configured provider."""
    provider = ModelProviderFactory.get_provider()
    
    try:
        result = await provider.chat_completion(request.messages)  
        if result is None:
            raise HTTPException(status_code=500, detail="Provider returned None")
        return {"message": {"content": result}}  # ✅ Return only the text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/logprobs")
async def logprobs_api(request: LogProbsRequest):
    """Handles log probability retrieval using the configured provider."""
    provider = ModelProviderFactory.get_provider()
    
    try:
        result = await provider.logprobs(request.prompt) 
        if result is None:
            raise HTTPException(status_code=500, detail="Provider returned None")
        return {"logprobs": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

