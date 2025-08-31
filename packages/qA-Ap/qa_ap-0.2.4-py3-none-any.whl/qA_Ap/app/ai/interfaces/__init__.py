from abc import ABC, abstractmethod

class AIInterface(ABC):
    """
    Abstract base class for AI interfaces.
    """
    @abstractmethod
    def query(self, prompt: str, history: list[dict[str,str]] = None, metadatas: dict = None) -> None:
        pass

    def format_history(self, history: list[dict[str,str]]):
        """
        Format the history list to fit the specific AIInterface used.
        """
        return history


class AIStreamResponse(ABC):
    """
    Abstract base class for AI stream responses.
    """
    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def __next__(self):
        pass