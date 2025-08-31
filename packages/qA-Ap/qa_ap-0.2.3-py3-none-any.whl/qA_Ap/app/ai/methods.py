from ...globals import globals
from .vectorstore import VectorStore
from .interfaces import AIStreamResponse

def vectorize_documents() -> None:
    """
    Create a vector store from all documents then save it in the database.

    Raises:
        RuntimeError: If vectorization or saving fails.
    """
    try:
        documents = globals.database.get_all_documents_data()
        print(f"{len(documents)} documents")
        globals.vectorstore = VectorStore(
            documents=documents, 
            sentence_transformers=globals.path_to_emmbeddings_model
        )
        globals.database.write_vector_store(globals.vectorstore.as_bytes)
        print("Vector store saved")
    except Exception as e:
        raise RuntimeError(f"Failed to vectorize documents: {e}")


def initialize_vector_store() -> None:
    """
    Initializes the vector store from the database, or creates it if not found or fails.
    """
    try:
        bytes_data = globals.database.get_vector_store()
        globals.vectorstore = VectorStore.from_bytes(
            data=bytes_data, 
            sentence_transformers=globals.path_to_emmbeddings_model
        )
        print(f"Vector store loaded.")
    except Exception as e:
        print(f"Failed to load vector store: {e}. Rebuilding vector store.")
        vectorize_documents()


@staticmethod
def _context_from_query_results(results: list[dict[str, any]]) -> str:
    """
    Builds a context string from query results for prompt construction.

    Args:
        results (list[dict[str, any]]): list of query result dictionaries.

    Returns:
        str: Formatted context string.
    """
    context = ""
    for i, result in enumerate(results):
        context += f"""Document {i+1} - {result["metadata"]["title"]}:
    {result["document"]}


    """
    return context

@staticmethod
def _metadata_from_query_results(results: list[dict[str, any]]) -> str:
    """
    Builds a context string from query results for prompt construction.

    Args:
        results (list[dict[str, any]]): list of query result dictionaries.

    Returns:
        str: Formatted context string.
    """
    metadatas = {}

    for result in results:
        metadatas[result["metadata"]["title"]] = result["metadata"]
        
    return metadatas

def query(query: str, history: list[dict[str,str]] = None, include_metadata: bool = False) -> AIStreamResponse:
    """
    Queries the vector store and generates a response using the LLM.

    Args:
        query (str): The user's query.

    Returns:
        str: The generated response from the LLM.

    Raises:
        RuntimeError: If querying or LLM generation fails.
    """
    try:
        
        if globals.vectorstore is None:
            print("WARNING: Vector store is not initialized. [qA_Ap.app.ai.methods.query]")
            results = []
        else:
            results = globals.vectorstore.query(query)
        
        prompt = globals.system_prompt.format(
            object_of_search = globals.object_of_search,
            context=_context_from_query_results(results),
            question=query
        )

        metadatas = _metadata_from_query_results(results) if include_metadata else None
        response: AIStreamResponse = globals.ai_interface.query(prompt,history,metadatas)

        return response
    except Exception as e:
        raise RuntimeError("An error occurred while processing your query.")
