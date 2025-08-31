# openai_llm.py
import os
import openai
from .base import BaseLLM

class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str = None, model_name: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required.")
        openai.api_key = self.api_key
        self.model_name = model_name

    def ask(self, query: str, context: str = None) -> str:
        prompt = f"{context}\n\nQuestion: {query}" if context else query
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
