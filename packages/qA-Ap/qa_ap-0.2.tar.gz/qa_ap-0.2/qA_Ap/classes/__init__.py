import json
import oyaml


class Document:
    """
    This is a class representing a document.
    
    Attributes:
        title (str): The title of the document.
        links (list[str]): A list of URLs or references to where the document can be accessed.
        tags (list[str]): A list of tags to which the document belongs.
        pictures (list[str]): A list of image URLs or paths to pictures of the document.
        notes (list[str]): The list of note_title names if any.
        content (str): The text content of the document.
    
    Methods:
        from_text(raw: str) -> Document: Creates a new Document object from text input.
        from_json(raw: str) -> Document: Creates a new Document object from JSON input.
        catalog_entry -> dict: Returns a short dict representation as it is stored in the catalog.
        json -> str: Returns the JSON representation of the document as it is used in the REST API.
        text -> str: Returns the text representation of the document as it is store in the database.
    """
    
    def __init__(self, title=None, content=None, metadatas={}):
        self.title = title
        self.content = content
        self.metadatas = metadatas
    
    @classmethod
    def from_text(cls, title: str, raw_content: str) -> 'Document':
        try:
            metas, separator, text = raw_content.partition("###")

            # If a separator is found in the file parse the yaml metadata before it
            if separator:       
                metadatas = oyaml.safe_load(metas)
            else:
                metadatas = {}

            content = text.strip()

            return cls(title=title, content=content, metadatas=metadatas)
        except Exception as e:
            print("Le fichier est mal formatté",e)
    
    @classmethod
    def from_json(cls, raw_content: str) -> 'Document':
        try:
            data = json.loads(raw_content)
            title = data['title']
            content = data['content']
            metadatas = data['metadatas']
            return cls(title=title, content=content, metadatas=metadatas)
        except Exception as e:
            print("Le JSON est invalide",e)
    
    @property
    def catalog_entry(self) -> dict:
        entry = {
            'title': self.title,
            'content': self.content[:300],
            'metadatas':self.metadatas
        }
        return entry
    
    @property
    def dict(self) -> dict:
        data = {
            'title': self.title,
            'content': self.content,
            'metadatas':self.metadatas
        }
        return data
    
    @property
    def text(self) -> str:
        yaml_metas = oyaml.safe_dump(self.metadatas)
        return f"{yaml_metas}\n###\n\n{self.content}"
    


    
class Note:
    """
        A class to represent a note of a document.

        Attributes:
            document (str): The name of the document being reviewed.
            note_title (str): The name of the note_title.
            pictures (list[str]): A list of paths to pictures related to the note.
            text (str): The text content of the note.

        Methods:
            from_text(cls, raw: str) -> 'Note':
                Creates a Note instance from a string containing YAML metadata and text content.

            from_json(cls, raw: str) -> 'Note':
                Creates a Note instance from a JSON string.

            json(self) -> dict:
                Returns the note data as a JSON string.

            text(self) -> str:
                Returns the note data as a string containing YAML metadata and text content.
    """

    def __init__(self, post_title: str, note_title: str, content: str, metadatas: dict[str,str] = None):
        """
            Initializes a new instance of the Note class.

            Args:
                document (str): The name of the document being reviewed.
                note_title (str): The name of the note_title.
                pictures (list[str]): A list of paths to pictures related to the note.
                content (str): The content content of the note.
        """
        self.document = post_title
        self.note_title = note_title
        self.content = content
        self.metadatas = metadatas

    @classmethod
    def from_text(cls, post_title: str, note_title: str, raw_content: str) -> 'Note':
        """
            Creates a Note instance from a string containing YAML metadata and text content.

            Args:
                raw (str): A string containing YAML metadata and text content.

            Returns:
                Note: A new instance of the Note class.

            Raises:
                Exception: If an unexpected error occurs.
        """
        try:
            metas, separator, text = raw_content.partition("###")

            # If a separator is found in the file parse the yaml metadata before it
            if separator:       
                metadatas = oyaml.safe_load(metas)
            else:
                metadatas = {}

            content = text.strip()

            return cls(
                post_title=post_title, 
                note_title=note_title, 
                content=content, 
                metadatas=metadatas
            )
        except Exception as e:
            print("Le fichier est mal formatté",e)

    @classmethod
    def from_json(cls, raw_content: str) -> 'Note':
        """
            Creates a Note instance from a JSON string.

            Args:
                raw (str): A JSON string containing note data.

            Returns:
                Note: A new instance of the Note class.

            Raises:
                Exception: If the JSON string is invalid.
        """
        try:
            data = json.loads(raw_content)
            return cls(
                document = data['document'], 
                note_title = data['note_title'], 
                content = data['content'],
                metadatas = data['metadatas']
                )
        except Exception as e:
            print("Le JSON est invalide",e)

    @property
    def dict(self) -> dict:
        """
            Returns the note data as a JSON string.

            Returns:
                dict: A dictionary containing the note data.
        """
        data = {
            'document': self.document,
            'note_title': self.note_title,
            'content': self.content,
            'metadatas': self.metadatas
        }
        return data

    @property
    def text(self) -> str:
        """
            Returns the note data as a string containing YAML metadata and text content.

            Returns:
                str: A string containing YAML metadata and text content.
        """
        yaml_metas = oyaml.safe_dump(self.metadatas)
        return f"{yaml_metas}\n###\n\n{self.content}"