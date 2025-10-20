"""LLM client for OpenRouter integration."""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Client for interacting with LLMs via OpenRouter."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """Initialize LLM client."""
        self.model = model or os.getenv("DEFAULT_MODEL", "meta-llama/llama-3.3-8b-instruct:free")
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. "
                "Set OPENROUTER_API_KEY in .env file or pass as argument."
            )
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
    
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        context: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, any]:
        """Generate a response from the LLM."""
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Relevant context from educational documents:\n\n{context}"
            })
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                "response": content,
                "tokens_used": tokens_used,
                "model": self.model,
                "finish_reason": response.choices[0].finish_reason
            }
        
        except Exception as e:
            return {
                "response": None,
                "error": str(e),
                "model": self.model,
                "tokens_used": 0
            }
    
    def set_model(self, model: str):
        """Change the model being used."""
        self.model = model
        return self


FREE_MODELS = {
    "llama-3.3-8b": "meta-llama/llama-3.3-8b-instruct:free",  # Recommended
    "gemma-2-9b": "google/gemma-2-9b-it:free", 
    "phi-3-mini": "microsoft/phi-3-mini-128k-instruct:free",
    "qwen-7b": "qwen/qwen-2-7b-instruct:free",
}

PAID_MODELS = {
    "gpt-3.5": "openai/gpt-3.5-turbo",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "claude-haiku": "anthropic/claude-3-haiku",
    "claude-sonnet": "anthropic/claude-3.5-sonnet",
}
