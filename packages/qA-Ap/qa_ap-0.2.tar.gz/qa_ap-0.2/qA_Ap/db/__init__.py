from abc import ABC, abstractmethod

class qaapDB(ABC):
    """
        Abstract base class for qA_Ap databases.
    """

    # ============================== CHECK METHODS

    @abstractmethod
    def document_exists(self, document_title: str) -> bool:
        pass

    @abstractmethod
    def comment_exists(self, document_title: str, note_title: str) -> bool:
        pass

    @abstractmethod
    def attribute_exists(self, attribute: str) -> bool:
        pass

    # ============================== GET METHODS

    @abstractmethod
    def get_catalog(self) -> str:
        pass

    @abstractmethod
    def get_attribute_values(self, attribute: str) -> str:
        pass

    @abstractmethod
    def get_document(self, document_title: str) -> str:
        pass

    @abstractmethod
    def get_document_medias(self, document_title: str, includes: list[str] = []) -> list[str]:
        pass

    @abstractmethod
    def get_notes_for_document(self, document_title: str, perpage: int = 0, page: int = 0) -> list[tuple[str, str, str]]:
        pass

    @abstractmethod
    def get_note_medias(self, document_title: str, note_title: str, includes: list[str] = []) -> list[str]:
        pass

    # ============================== WRITE METHODS

    @abstractmethod
    def write_catalog(self, json: str) -> bool:
        pass

    @abstractmethod
    def write_document(self, document_title: str, content: str, medias: list[tuple[str, str]]) -> bool:
        pass

    @abstractmethod
    def write_note(self, document_title: str, note_title: str, content: str, medias: list[tuple[str, str]]) -> bool:
        pass

    @abstractmethod
    def write_attribute(self, attribute: str, data: str) -> bool:
        pass

    @abstractmethod
    def add_attribute_values(self, attribute: str, data: list[str]) -> bool:
        pass

    # ============================== RAG METHODS

    @abstractmethod
    def get_all_documents_data(self) -> list[dict[str, str]]:
        pass

    @abstractmethod
    def get_vector_store(self) -> bytes:
        pass

    @abstractmethod
    def write_vector_store(self, bytes_data: bytes) -> bool:
        pass