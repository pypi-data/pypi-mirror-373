# claude_llm.py
import os
import requests
from .base import BaseLLM
class ClaudeLLM(BaseLLM):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required.")
        self.url = "https://api.anthropic.com/v1/complete"

    def ask(self, query: str, context: str = None) -> str:
        prompt = f"{context}\n\n{query}" if context else query
        payload = {"model": "claude-3", "prompt": prompt, "max_tokens": 1000, "temperature": 0.7}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(self.url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['completion'].strip()
