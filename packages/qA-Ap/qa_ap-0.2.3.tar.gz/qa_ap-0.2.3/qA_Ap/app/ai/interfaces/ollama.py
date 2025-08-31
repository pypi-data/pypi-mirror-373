import ollama
from . import AIInterface, AIStreamResponse

class OllamaAIInterface(AIInterface):
    """
    Concrete AI interface using Ollama.
    """
    def __init__(self, model_name: str = ""):
        """
        Initializes the Ollama AI interface with a model name.
        
        Args:
            model_name (str): The name of the Ollama model to use.
        """
        self.model_name = model_name

    def query(self, query: str, history: list[dict[str,str]] = None, metadatas: dict = None) -> AIStreamResponse:

        messages = []

        if history:
            messages.extend(self.format_history(history))

        messages.append({
                    "role": "user",
                    "content": query
                })
        
        stream = ollama.chat(
            model=self.model_name,
            think=True,
            messages=messages,
            stream=True
        )

        return OllamaAIStreamResponse(stream, metadatas)
        

class OllamaAIStreamResponse(AIStreamResponse):
    """
    Concrete AI stream response for Ollama.
    """
    def __init__(self, stream, metadatas):
        """
        Initializes the Ollama AI stream response.
        
        Args:
            stream: The stream from the Ollama client.
        """
        self.stream = stream
        self.metadatas = metadatas

    def __iter__(self):
        """
        Iterates over the stream and yields responses.
        
        Yields:
            str: The content of each response chunk.
        """
        for chunk in self.stream:
            yield chunk['message']['content'] or ""
            
    def __next__(self):
        """
        Returns the next item from the stream.
        
        Returns:
            str: The content of the next response chunk.
        """
        try:
            return next(self.stream)['message']['content'] or ""
        except StopIteration:
            raise StopIteration("No more items in the stream.")