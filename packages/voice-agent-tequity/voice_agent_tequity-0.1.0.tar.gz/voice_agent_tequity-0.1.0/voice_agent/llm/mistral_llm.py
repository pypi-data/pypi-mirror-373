# mistral_llm.py
import os
from .base import BaseLLM
import requests

class MistralLLM(BaseLLM):
    def __init__(self, api_key: str = None, model_name: str = "mistral-7b"):
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required.")
        self.model_name = model_name
        self.url = f"https://api.mistral.ai/v1/completions"

    def ask(self, query: str, context: str = None) -> str:
        prompt = f"{context}\n\n{query}" if context else query
        payload = {"model": self.model_name, "prompt": prompt, "max_tokens": 1000, "temperature": 0.7}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['text'].strip()
