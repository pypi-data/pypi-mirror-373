# llm_factory.py
from .gemini_llm import GeminiLLm
from .openai_llm import OpenAILLM
from .ollma_llm import OllamaLLM
from .openrouter_service_llm import OpenRouterLLM
from .claude_llm import ClaudeLLM
from .custom_llm import CustomLLm

class LLMFactory:
    @staticmethod
    def get_llm(llm_type: str, **kwargs):
        llm_type = llm_type.lower()
        if llm_type == "gemini":
            return GeminiLLm(api_key=kwargs.get("api_key"))
        elif llm_type == "openai":
            return OpenAILLM(api_key=kwargs.get("api_key"), model_name=kwargs.get("model_name", "gpt-4"))
        elif llm_type == "ollama":
            return OllamaLLM(model_name=kwargs.get("model_name", "gemma3"), api_key=kwargs.get("api_key"))
        elif llm_type == "openrouter":
            return OpenRouterLLM(api_key=kwargs.get("api_key"), model_name=kwargs.get("model_name", "openrouter-model"))
        elif llm_type == "claude":
            return ClaudeLLM(api_key=kwargs.get("api_key"), model_name=kwargs.get("model_name", "claude-3"))
        elif llm_type == "custom":
            return CustomLLm(api_key=kwargs.get("api_key"), model_url=kwargs.get("model_url"))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")
