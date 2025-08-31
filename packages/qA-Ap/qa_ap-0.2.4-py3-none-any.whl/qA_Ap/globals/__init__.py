from ..db import qaapDB
from ..app.ai.interfaces import AIInterface
from ..app.ai.vectorstore import VectorStore

class _globals():
    """
        This module stores the variables needed accross the application.
        
        - Database is a qA_Ap.db.qaapDB instance used as database.
        - AIInterface is a qA_Ap.app.ai.interfaces.AIInterface used to query a LMM.
        - VectorStore is The qA_Ap.app.ai.VectorStore instance used to store embedded documents and retrieve them by similarity search
    """

    database: qaapDB = None
    ai_interface: AIInterface = None
    vectorstore: VectorStore = None

    path_to_emmbeddings_model: str = ""
    system_prompt: str = ""
    object_of_search: str = ""

globals = _globals