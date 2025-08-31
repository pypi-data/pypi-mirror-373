import json

from ..globals import globals
from ..classes import Document


def compile_catalog() -> None:
    """
        Compiles "catalog_entry" representations of all documents in one JSON file
        and writes it to the database.

        Raises:
            RuntimeError: If there is an error during compilation.
    """
    try:
        data: list[dict[str, str]] = globals.database.get_all_documents_data()

        documents: list[dict] = [
            Document.from_text(raw["title"], raw["content"]).catalog_entry for raw in data
        ]
    
        globals.database.write_catalog(json.dumps(documents))
    except Exception as e:
        raise RuntimeError(f"Failed to compile catalog: {str(e)}")


def compile_attribute(attribute: str) -> None:
    """
        Compiles all unique attribute found in the catalog in a single file
        with each tag on a new line and writes it to the database.

        Raises:
            RegisterError: If there is an error during compilation or writing.
    """
    try:
        catalog = json.loads(globals.database.get_catalog())
        values: list[list[str]|str] = [document["metadatas"][attribute] for document in catalog if (attribute in document["metadatas"])]
        
        flattened = []
        
        for v in values:
            if isinstance(v, list):
                flattened.extend(v)
            else:
                flattened.append(v)

        unique_values = set(flattened)

        globals.database.write_attribute(attribute, "\n".join(unique_values))
    except Exception as e:
        raise RuntimeError(f"Failed to compile attribute '{attribute}' values: {str(e)}")
    


def find_documents_by_metadata(attribute: str, value: str) -> list[dict]:
    """
        Finds all documents in the catalog that have a specific metadata attribute
        containing a specific value.

        Args:
            attribute (str): The metadata attribute to search for.
            value (str): The value to search for within the attribute.

        Returns:
            list[dict]: A list of documents that match the criteria.

        Raises:
            RegisterError: If there is an error during the search.
    """
    try:
        catalog = json.loads(globals.database.get_catalog())
        results = [
            document for document in catalog
            if attribute in document["metadatas"] and value in document["metadatas"][attribute]
        ]
        return results
    except Exception as e:
        raise RuntimeError(f"Failed to find documents by metadata '{attribute}': {str(e)}")