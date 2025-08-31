from abc import ABC, abstractmethod
from dataclasses import dataclass

class VectorStore(ABC):
    """
    An abstract base class for vector stores.
    """

    @abstractmethod
    def __init__(self, documents: list[dict[str, str]], sentence_transformers: str):
        """
        Initializes the VectorStore with optional documents.

        Args:
            documents (list[dict[str, str]], optional): list of documents with 'title' and 'content'.
        """
        pass

    @abstractmethod
    def _setup(self, documents: list[dict[str, str]]) -> tuple[any, list[str], list[str], list[dict[str, str]]]:
        """
        Splits documents into chunks of maximum 1000 characters.

        For each chunk:
            create a unique ID string made of the document title and chunk index,
            and a metadata dict with the document title.

        Creates an index for the embeddings.

        Args:
            documents (list[dict[str, str]]): list of documents.

        Returns:
            tuple: (any-index-, list of chunks, list of ids, list of metas)
        """
        pass

    @abstractmethod
    def query(self, query: str) -> list[dict]:
        """
        Query the vector store for the most similar document chunks.

        Args:
            query (str): The query string.

        Returns:
            list[dict]: list of results with document, metadata, and distance.

        Raises:
            ValueError: If the vector store is not initialized.
            RuntimeError: If the query fails.
        """
        pass

    @property
    @abstractmethod
    def metas_json(self) -> str:
        """
        Returns a JSON string of ids, metas, and documents.

        Returns:
            str: JSON representation.
        """
        pass

    @property
    @abstractmethod
    def as_bytes(self) -> bytes:
        """
        Serializes the vector store to bytes.

        Returns:
            bytes: Serialized vector store.
        """
        pass

    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes, sentence_transformers: str) -> "AbstractVectorStore":
        """
        Deserializes a VectorStore from bytes.

        Args:
            raw (bytes): Serialized vector store.

        Returns:
            AbstractVectorStore: The deserialized instance.
        """
        pass



@dataclass
class VectorStoreData():
    """
    An base class for vector store data.
    """
    store :any
    """
    The index for the embeddings.

    Returns:
        any: The index.
    """
    ids: list[str]
    """
    The list of document chunks.

    Returns:
        list[str]: The list of document chunks.
    """
    documents: list[str]
    """
    The list of document chunks.

    Returns:
        list[str]: The list of document chunks.
    """
    metadatas: list[dict[str,str]]
    """
    The list of metadata dictionaries.

    Returns:
        list[dict[str, str]]: The list of metadata dictionaries.
    """