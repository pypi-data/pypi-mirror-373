import pickle
import pickletools
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from semantic_text_splitter import TextSplitter

class VectorStore():
    """
    A class for storing and querying document embeddings using FAISS and SentenceTransformer.
    """

    def __init__(self, documents: list[dict[str, str]], sentence_transformers: str):
        """
        Initializes the VectorStore with optional documents.

        Args:
            documents (list[dict[str, str]], optional): List of documents with 'title' and 'content'.
        """
        try:
            self.model = SentenceTransformer(sentence_transformers)
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {str(e)}")
        if documents:
            try:
                self.store, self.documents, self.ids, self.metadatas = self._setup(documents)
            except Exception as e:
                raise RuntimeError(f"Failed to set up vector store: {str(e)}")
        else:
            self.documents = []
            self.store = None
            self.ids = []
            self.metadatas = []

    def _setup(self, documents: list[dict[str, str]]) -> tuple[faiss.IndexFlatL2, list[str], list[str], list[dict[str, str]]]:
        """
        Splits documents into chunks of maximum 1000 characters.

        For each chunk:
            create a unique ID string made of the document title and chunk index,
            and a metadata dict with the document title.

        Creates a FAISS index for the embeddings.

        Args:
            documents (list[dict[str, str]]): List of documents.

        Returns:
            tuple: (FAISS index, list of chunks, list of ids, list of metas)
        """
        try:
            text_splitter = TextSplitter(1000)
            chunks = []
            ids = []
            metadatas = []
            for document in documents:
                raw_chunks = text_splitter.chunks(document["content"])
                print(f"{len(raw_chunks)} chunks")
                for i, chunk in enumerate(raw_chunks):
                    chunks.append(chunk)
                    ids.append(f"{document['title']}-{i}")
                    meta_entry = {
                        "title": document["title"],
                    }
                    meta_entry.update(document["metadata"])
                    metadatas.append(meta_entry)

            embeddings = self.model.encode(chunks)
            embeddings = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings)
            store = faiss.IndexFlatL2(embeddings.shape[1])
            store.add(embeddings)

            return store, chunks, ids, metadatas
        except Exception as e:
            raise RuntimeError(f"Error during setup: {str(e)}")
    
    def query(self,query: str) -> list[dict]:
        """
        Query the vector store for the most similar document chunks.

        Args:
            query (str): The query string.

        Returns:
            list[dict]: List of results with document, metadata, and distance.
            
        Raises:
            ValueError: If the vector store is not initialized.
            RuntimeError: If the query fails.
        """
        if self.store is None or self.documents is None:
            print("WARNING: Vector store is empty ! [qA_Ap.app.ai.vectorstore.VectorStore.query]")
            return []
        
        try:
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')

            k = 5
            distances, indices = self.store.search(query_embedding, k)

            results = []
            for i, idx in enumerate(indices[0]):
                results.append({
                    "document": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "distance": distances[0][i]
                })

            return results
        except Exception as e:
            raise RuntimeError(f"Failed to query vector store: {str(e)}")

    @property
    def metas_json(self) -> str:
        """
        Returns a JSON string of ids, metas, and documents.

        Returns:
            str: JSON representation.
        """
        try:
            return json.dumps({"ids":self.ids,"metadatas":self.metadatas,"documents":self.documents})
        except Exception as e:
            raise RuntimeError(f"Failed to serialize metadatas to JSON: {str(e)}")


    @property
    def as_bytes(self) -> bytes:
        """
        Serializes the vector store to bytes.

        Returns:
            bytes: Serialized vector store.
        """
        try:
            data = VectorStoreData(self.store, self.ids, self.documents, self.metadatas)
            raw: bytes = pickle.dumps(data)
            return pickletools.optimize(raw)
        except Exception as e:
            raise RuntimeError(f"Failed to serialize vector store: {str(e)}")

    @classmethod
    def from_bytes(cls,data: bytes, sentence_transformers: str) -> "VectorStore":
        """
        Deserializes a VectorStore from bytes.

        Args:
            raw (bytes): Serialized vector store.

        Returns:
            VectorStore: The deserialized instance.
        """
        try:
            data = pickle.loads(data)
            instance = cls(
                documents=None,
                sentence_transformers=sentence_transformers
            )
            instance.ids = data.ids
            instance.metadatas = data.metadatas
            instance.documents = data.documents
            instance.store = data.store
            return instance
        except Exception as e:
            raise RuntimeError(f"Failed to deserialize vector store: {str(e)}")


from dataclasses import dataclass
@dataclass
class VectorStoreData():
    """
    Dataclass for storing vector store data for serialization.
    """
    store :faiss.IndexFlatL2
    ids: list[str]
    documents: list[str]
    metadatas: list[dict[str,str]]