from .app.catalog import compile_catalog, compile_attribute
from .db import qaapDB, flatfiledb
from .app.ai.methods import initialize_vector_store
from .app.ai.methods import query as _query
from .app.ai.interfaces import AIInterface, ollama
from .web.api import server as _server
from .web import activate_integrated_frontend
import globals


"""
========================================
  qA_Ap - query About Anything package
========================================

Author: Martin Ashton-Lomax
Github: https://github.com/Fleurman/qA_Ap
License: MIT
Version: 0.1

========================================

A Q&A application powered by LLMs and RAG on custom data.

Modules:
- db: Database interfaces and implementations.
- app: Core application logic including AI interactions and catalog management.
- api: API server for handling requests.
- state: Global state management.
- classes: Data structures and errors.
- settings: Configuration settings for the application.

"""



default_system_prompt = """
    You are an assistant for question-answering tasks.
    Your role is to guide the user to find {object_of_search} for its need.
    Use the following pieces of retrieved context to answer the question if it matches the user needs.
    Do not mention any context that do not matches the question.
    Use your general knowledge if the context is lacking.
    Use the same language as the question and keep the answer concise.
    After your answer, list all relevant documents name between brackets.

    Question: {question} 
    Context: {context}
    Answer:
"""

def init(
        database: str | qaapDB = "data/qaap_db",
        ai: AIInterface | str = "qwen3:0.6b",
        embeddings_model: str = "Qwen3-Embedding-0.6B",
        object_of_search: str = "solutions",
        system_prompt: str = default_system_prompt,
        api_server: int | dict = 8080,
        allow_post: bool = False,
        frontend: bool = False,
        catalog: bool = True,
        attributes: list[str] = None
):
    """
    Initializes the application with the specified configurations.

    This method sets up the database, AI interface, and other necessary components
    for the application. It also initializes the vector store and optionally starts
    the API server.

    Args:
        database (str | ottoDB.ottoDB, optional): The database to use. Can be a path to a flat file database (uses a FlatFileDB instance) or an instance of ottoDB. Defaults to "data/qaap_db".
        ai (AIInterface.AIInterface | str, optional): The AI interface to use. Can be a model name (uses an OllamaAIInterface) or an instance of AIInterface. Defaults to "qwen3:0.6b".
        embeddings_model (str, optional): The embeddings model to use via SentenceTransformer. Can be a local path or HuggingFace project name. Defaults to "Qwen3-Embedding-0.6B".
        object_of_search (str, optional): The object of search. Will be replaced in the system_prompt. Defaults to "solutions".
        system_prompt (str, optional): The system prompt to use. Defaults to qA_Ap.default_system_prompt.
        api_server (int | dict | False, optional): The port on wich to run the API server (bottle.py). If a dictionary is provided, it will be used as the server configuration. If False the server is not run. Defaults to 8080.
        auth (bool, optional): Whether to enable authentication on the API server POST endpoints. Defaults to False.
        frontend (bool, optional): Whether to run the integrated frontend interface. Defaults to False.

    Returns:
        None
    """
    globals.path_to_emmbeddings_model = embeddings_model
    globals.system_prompt = system_prompt
    globals.object_of_search = object_of_search

    if isinstance(database, qaapDB):
        globals.database = database
    elif isinstance(database, str):
        globals.database = flatfiledb.FlatFileDB(database)
    pass

    if isinstance(ai, AIInterface):
        globals.ai_interface = ai
    elif isinstance(ai, str):
        globals.ai_interface = ollama.OllamaAIInterface(model_name=ai)
    pass

    if allow_post == True:
        _server.post_auth_check = lambda: True

    if catalog == True:
        compile_catalog()

    if attributes:
        for attribute in attributes:
            compile_attribute(attribute)
    
    initialize_vector_store()
    
    if frontend == True:
        activate_integrated_frontend()

    if api_server:
        
        if isinstance(api_server, dict):
            _server.run(**dict)

        if isinstance(api_server,int):
            _server.run(host='0.0.0.0', port=api_server)


"""
aliases
"""
query = _query
server = _server


__all__ = [
    "database",
    "query",
    "server",
    "init",
    "compile_catalog",
    "compile_attribute"
]