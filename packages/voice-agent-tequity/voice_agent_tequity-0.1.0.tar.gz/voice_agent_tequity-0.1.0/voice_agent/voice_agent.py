import os
from dotenv import load_dotenv

from voice_agent.llm.gemini_llm import GeminiLLm
from voice_agent.llm.openai_llm import OpenAILLM
from voice_agent.llm.ollma_llm import OllamaLLM
from voice_agent.llm.openrouter_service_llm import OpenRouterLLM
from voice_agent.llm.claude_llm import ClaudeLLM
from voice_agent.llm.custom_llm import CustomLLm

load_dotenv()

class VoiceAgent:
    """
    Handles ONLY LLM selection and running prompts.
    No vector DB operations here.
    """

    def __init__(self, llm_type: str = "openai", **kwargs):
        """
        Args:
            llm_type (str): Type of LLM (gemini, openai, ollama, openrouter, claude, custom)
            **kwargs: Extra args passed to LLM constructors (e.g. api_key, model_name, model_url)
        """
        self.llm = self._get_llm(llm_type, **kwargs)

    def _get_llm(self, llm_type: str, **kwargs):
        llm_type = llm_type.lower()
        if llm_type == "gemini":
            return GeminiLLm(api_key=kwargs.get("api_key"))
        elif llm_type == "openai":
            return OpenAILLM(api_key=kwargs.get("api_key"), 
                             model_name=kwargs.get("model_name", "gpt-4"))
        elif llm_type == "ollama":
            return OllamaLLM(model_name=kwargs.get("model_name", "gemma3"), 
                             api_key=kwargs.get("api_key"))
        elif llm_type == "openrouter":
            return OpenRouterLLM(api_key=kwargs.get("api_key"), 
                                 model_name=kwargs.get("model_name", "openrouter-model"))
        elif llm_type == "claude":
            return ClaudeLLM(api_key=kwargs.get("api_key"), 
                             model_name=kwargs.get("model_name", "claude-3"))
        elif llm_type == "custom":
            return CustomLLm(api_key=kwargs.get("api_key"), 
                             model_url=kwargs.get("model_url"))
        else:
            raise ValueError(f"Unsupported LLM type: {llm_type}")

    def run_llm(self, prompt: str, **kwargs):
        """Run the selected LLM on a given prompt."""
        if not self.llm:
            raise RuntimeError("No LLM initialized.")
        print(f"[INFO] Running prompt on {self.llm.__class__.__name__}")
        from voice_agent.tts.evenlabs_tts import ElevenTTS
        tts = ElevenTTS(os.getenv("ELEVEN_API_KEY"))
        tts.speak(self.llm.ask(prompt, **kwargs))
        return self.llm.ask(prompt, **kwargs)


from voice_agent.gather.base import BaseVectorHandler

class TrainVoiceAgent(BaseVectorHandler):
    """
    Handles ONLY vector DB operations.
    Inherits from BaseVectorHandler which already has:
      - __init__(train, folder_path, email)
      - train_vector_db()
      - query()
    """

    def __init__(self, train=False, folder_path="./data_folder", email="user@example.com"):
        """
        Args:
            train (bool): If True, automatically upserts all TXT files at init.
            folder_path (str): Path to folder with training data
            email (str): Namespace for vector DB entries
        """
        super().__init__(train=train, folder_path=folder_path, email=email)

    def insert_data(self):
        """Explicit method for inserting data into vector DB."""
        print("[INFO] Inserting data into vector DB...")
        self.train_vector_db()

    def retrieve_data(self, query_text: str):
        """Explicit method for retrieving chunks from vector DB."""
        print("[INFO] Retrieving data from vector DB...")
        from voice_agent.llm.gemini_llm import GeminiLLm
        llm = GeminiLLm(api_key=os.getenv("GEMINI_API_KEY"))
        x=llm.ask(query_text,self.query(query_text))
        from voice_agent.tts.evenlabs_tts import ElevenTTS
        tts = ElevenTTS(os.getenv("ELEVEN_API_KEY"))
        tts.speak(x)
        return self.query(query_text)
