# openrouter_llm.py
import os
import requests
from .base import BaseLLM
class OpenRouterLLM(BaseLLM):
    def __init__(self, api_key: str = None, model_name: str = "openrouter-model"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key is required.")
        self.model_name = model_name
        self.url = "https://api.openrouter.ai/v1"

    def ask(self, query: str, context: str = None) -> str:
        messages = [{"role": "user", "content": f"{context}\n\n{query}"}] if context else [{"role": "user", "content": query}]
        payload = {"model": self.model_name, "messages": messages}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()


