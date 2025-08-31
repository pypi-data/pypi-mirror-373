# ollama_llm.py
import os
import requests
from .base import BaseLLM
class OllamaLLM(BaseLLM):
    def __init__(self, model_name: str = "gemma3", api_key: str = None):
        self.api_key = api_key or os.getenv("OLLAMA_API_KEY")
        if not self.api_key:
            raise ValueError("Ollama API key is required.")
        self.model_name = model_name
        self.url = f"http://localhost:11434/v1/models/{self.model_name}/generate"

    def ask(self, query: str, context: str = None) -> str:
        prompt = f"{context}\n\nQuestion: {query}" if context else query
        payload = {"inputs": [{"role": "user", "content": prompt}], "parameters": {"temperature": 0.7}}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content'].strip()
