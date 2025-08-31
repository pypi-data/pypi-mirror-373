import os
import requests
from .base import BaseLLM
class GeminiLLm(BaseLLM):
    """
    Simple Gemini API client to ask questions based on context.
    """

    def __init__(self, api_key: str = None):
        # You can pass API key here or rely on env variable
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required.")

        self.url = (
            f"https://generativelanguage.googleapis.com/v1beta/"
            f"models/gemini-1.5-flash:generateContent?key={self.api_key}"
        )

    def ask(self, query: str, context: str = None) -> str:
        """
        Ask Gemini a question with provided context.
        Returns the generated text as a string.
        """
        prompt = f"""
        Context:
        {context}

        Question:
        {query} make the answer as concise as possible. If the question is long, answer long; if short, provide at least 20 tokens.
        """

        payload = {
            "contents": [
                {"parts": [{"text": prompt.strip()}]}
            ]
        }

        try:
            response = requests.post(
                self.url,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            answer = data['candidates'][0]['content']['parts'][0]['text']

            # Clean up "Based on the provided text..." type messages
            if answer.lower().startswith("based on") or "provided text" in answer.lower():
                return answer.split(":", 1)[-1].strip()
            return answer.strip()

        except Exception as e:
            # Simply return error message if request fails
            return f"[Gemini Error]: {str(e)}"
