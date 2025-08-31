import  requests 

from .base import BaseLLM

class CustomLLm(BaseLLM):
     """Custom model hosted anywhere with API key and URL provided by user."""
     def __init__(self,api_key:str,model_url:str):
          self.api_key=api_key
          self.model_url=model_url

     def ask(self,query:str,context:str=None)->str:
            prompt=f"{context}\n\n{query}" if context else query
            headers={"Authorization": f"Bearer {self.api_key}"}
            response = requests.post(self.model_url, json={"prompt": prompt}, headers=headers)
            response.raise_for_status()
            return response.json().get("response", "").strip()

