from ..globals import database
from ..classes.errors import ExistsError, NotFoundError, RegisterError
from ..classes.errors.db import FileAlreadyExistsError, WriteInDatabaseError
from ..classes import Document, Note


def register_new_attribute_value(attribute: str, value: str) -> bool:
    """
        Registers a new attribute value in the database.

        Args:
            attribute (str): The name of the attribute to register.
            value (str): The new value of the attribute.

        Returns:
            bool: True if the attribute was registered successfully or if it already exists.

        Raises:
            RegisterError: If there is an error during registration.
    """
    try:
        database.add_attribute_values(attribute, value)
    except Exception as e:
        raise RegisterError(f"Failed to register attribute '{attribute}' with new value '{value}': {str(e)}")

    return True


def register_new_comment(note: Note) -> bool:
    """
        Registers a new note for a document.

        Args:
            note (Note): The note to register.

        Returns:
            bool: True if the note was registered successfully.

        Raises:
            NotFoundError: If the document does not exist.
            ExistsError: If the note already exists.
            RegisterError: If there is an error during registration.
    """
    try:
        database.write_comment(
            note.document, note.note_title, note.metadatas, note.text
        )
    except FileAlreadyExistsError as e:
        raise ExistsError(f"Note already exists: {str(e)}")
    except FileNotFoundError as e:
        raise NotFoundError(f"Document not found: {str(e)}")
    except Exception as e:
        raise RegisterError(f"Failed to register note: {str(e)}")

    return True


def register_new_post(document :Document) -> bool:
    """
        Registers a new document in the database.

        Args:
            document (Document): The document to register.

        Returns:
            bool: True if the document was registered successfully.

        Raises:
            NotFoundError: If the document does not exist.
            RegisterError: If there is an error during registration.
    """
    try:
        database.write_post(
            document.title, document.icon, document.metadatas, document.content
        )
    except FileNotFoundError as e:
        raise NotFoundError(f"Document '{document.title}' not found.")
    except FileAlreadyExistsError as e:
        raise ExistsError(f"Document already exists: {str(e)}")
    except Exception as e:
        raise RegisterError(f"Failed to register document: {str(e)}")

    return True
