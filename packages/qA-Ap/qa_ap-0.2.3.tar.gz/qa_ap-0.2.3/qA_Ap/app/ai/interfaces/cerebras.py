from cerebras.cloud.sdk import Cerebras
from . import AIInterface,AIStreamResponse

class CerebrasAIInterface(AIInterface):
    """
    Concrete AI interface using Cerebras.
    """

    def __init__(self, key: str = None, model_name: str = ""):
        """
        Initializes the Cerebras AI interface.
        """
        self.client = Cerebras(api_key=key)
        self.model_name = model_name

    def query(self, query: str, history: list[dict[str,str]] = None, metadatas: dict = None) -> None:

        messages = []

        if history:
            messages.extend(self.format_history(history))

        messages.append({
                    "role": "user",
                    "content": query
                })

        stream = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            stream=True,
            max_completion_tokens=65536,
            temperature=1,
            top_p=1
        )

        return CerebrasAIStreamResponse(stream, metadatas)


class CerebrasAIStreamResponse(AIStreamResponse):
    def __init__(self, stream, metadatas):
        """
        Initializes the Cerebras AI stream response.
        
        Args:
            stream: The stream from the Cerebras client.
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
            yield chunk.choices[0].delta.content or ""

    def __next__(self):
        """
        Returns the next item from the stream.
        
        Returns:
            str: The content of the next response chunk.
        
        Raises:
            StopIteration: If there are no more items in the stream.
        """
        try:
            return next(self.stream).choices[0].delta.content or ""
        except StopIteration:
            raise StopIteration