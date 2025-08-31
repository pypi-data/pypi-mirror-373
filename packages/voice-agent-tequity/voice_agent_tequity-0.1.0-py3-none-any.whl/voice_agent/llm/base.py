from abc import  ABC, abstractmethod

class BaseLLM(ABC):
    #### abstract method for asking questions for all the llms """"###
    @abstractmethod
    def ask(self, question: str, context: str) -> str:
        
        pass
