import json
from pathlib import Path

import oyaml
from pdoc import pdoc
from bottle import Bottle, response, request, HTTPResponse, static_file

from ..globals import globals
from ..classes import Document, Note
from ..app.ai.methods import query
from ..app.catalog import compile_catalog, compile_attribute

CURRENT_PATH = Path(__file__).parent.resolve()

server = Bottle()
""" 
    A Bottle server instance.
    It is accessible as `qA_Ap.server`.
"""


# ============================================================== Authentication Wrappers


post_auth_check = lambda: False
""" 
A method variable called before each POST request.
It must return a bool that indicates wether or not the request can be made. 
By default always returns `False` unless `allow_post` is set to `True` in the `qA_Ap.init()` method.
Redefine this variable to implement your authentication.
```qA_Ap.server.post_auth_check = your_method```
"""
stream_auth_check = lambda: True
""" 
A method  variable called before each `api/stream` endpoint request.
It must return a bool that indicates wether or not the request can be made.
By default always returns `True`.
Redefine this variable to implement your stream endpoint authentication.
```qA_Ap.server.stream_auth_check = your_method```
"""

def post_auth_wrapper(func):
    """
    A decorator to each POST endpoints.
    Calls the post_auth_check to checks wheter or not the request is authenticated.
    """

    def wrapper(*args, **kwargs):
            if post_auth_check() == False:
                return HTTPResponse(status=401, body=json.dumps({"error": "Unauthorized"}))
            
            return func(*args, **kwargs)
    
    return wrapper

def stream_auth_wrapper(func):
    """
    A decorator to each the 'api/stream' endpoint.
    Calls the stream_auth_check to checks wheter or not the request is authenticated.
    """

    def wrapper(*args, **kwargs):
            if stream_auth_check() == False:
                return HTTPResponse(status=401, body=json.dumps({"error": "Unauthorized"}))
            
            return func(*args, **kwargs)
    
    return wrapper


# ============================================================ DOCS ENDPOINTS

@server.get('/api/docs')
def get_docs() -> str:
    """
    # GET `/api/docs`

    Returns the api documentation generated with [**pDoc**](https://pdoc.dev/).

    """
    return static_file("api_docs.html", root=CURRENT_PATH)

# ============================================================== GET ENDPOINTS

@server.get('/api/catalog')
def get_catalog() -> str:
    """
    # GET `/api/catalog`

    Returns the catalog as JSON.

    The catalog is a list of all documents with their metadata and a short excerpt.

    ## 200 response:
    ```json
        [
            {
                "title": "Document Title",
                "metadata": {
                    "links": ["link1", "link2"],
                    "attributes": ["attribute1", "attribute2"],
                    },
                "excerpt": "This is a short excerpt of the document..."
            },
            ...
        ]
    ```

    """
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'
    try:
        return globals.database.get_catalog()
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})

@server.get('/api/document/<name>')
def get_document_by_name(name: str) -> str:
    """
    # GET `/api/document/<name>`

    Returns a document by name.
    Returns an error message if the document is not found or if an error occurs.
    
    ## 200 response:
    ```json 
    {
        "title": "Document Title",
        "content": "Full content of the document...",
        "metadata": {
            "links": ["link1", "link2"],
            "attributes": ["attribute1", "attribute2"],
        }
    }
    ```

    ## Error response:
    ```json
        {"error": "<error message>"}
    ```
    """
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'
    try:
        document = globals.database.get_document(name)
        return json.dumps(Document.from_text(name, document).dict)
    except Exception as e:
        response.status = 404
        return json.dumps({"error": str(e)})

@server.get('/api/notes/<post_title>')
def get_notes_for_post(post_title: str) -> str:
    """
    # GET `/api/notes/<post_title>`

    Returns all notes for a document as JSON.

    ## 200 response:
    ```json
    [
        {
            "note_title": "User1",
            "content": "Note content...",
            "metadata": {
                "rating": 5,
            }
        },
        ...
    ]
    ```

    ## Error response:
    ```json
    {"error": "<error message>"}
    ```
    """
    response.headers['Content-Type'] = 'application/json'
    response.headers['Cache-Control'] = 'no-cache'
    try:
        notes = globals.database.get_notes_for_post(post_title)
        return json.dumps([Note.from_text(note_title, document, content).dict for (content, document, note_title) in notes])
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})

@server.get('/api/attributes/<attribute_name>')
def get_attributes(attribute_name: str) -> str:
    """
    # GET `/api/attributes/<attribute_name>`

    Returns all existing values for the specified attribute as JSON.

    ## 200 response:
    ```json
    [
        "attribute1",
        "attribute2",
        ...
    ]
    ```

    ## Error response:
    ```json
    {"error": "<error message>"}
    ```
    """
    response.headers['Content-Type'] = 'application/json'
    try:
        cats = globals.database.get_attribute_values(attribute_name).split("\n")
        return json.dumps(cats)
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})


# ============================================================== POST ENDPOINTS

@server.post('/api/document')
@post_auth_wrapper
def post_post() -> str:
    """
    # POST `/api/document`

    Registers a new document.

    ## Request body:
    ```json
    {
        "title": <str>,
        "medias": <list[str]>,
        "content": <yaml str> | <str>
        "metadata": <dict[str,str]>
    }
    ```
    
    If no `metadata` field is given the document content can be in YAML format with optional metadata prefixed.

    ## Document content example with metadata:
    ```yaml
    medias: 
        - image1.png
        - image2.png
    tags:
        - tag1
        - tag2
    ###
    
    This is the text content of the document.
    ```

    If the `metadata` field is given, the yaml formatted fields are prefixed to the content automatically.

    ## 200 response:
    ```json
    {
        "success": true,
        "message": "The document <post_title> is created"
    }
    ```

    ## Error response:
    ```json
    {"error": "<error message>"}
    ```
    """
    response.headers['Content-Type'] = 'application/json'
    try:
        data = request.json
        required = ["title", "content"]
        if not data or not all(k in data for k in required):
            response.status = 400
            return json.dumps({"error": "Missing required fields '[title, content]'"})
        title = data["title"]
        content = data["content"]
        metadatas = data.get("metadata", False)
        if metadatas:
            yaml_metas = oyaml.safe_dump(metadatas)
            content = f"{yaml_metas}\n###\n\n{content}"
        globals.database.write_post(title, content, data.get("medias", []))
        return json.dumps({"message": f"The document {title} is created"})
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})


@server.post('/api/note')
@post_auth_wrapper
def post_comment() -> str:
    """
    # POST `/api/note`

    Registers a new note.

    ## Request body:
    ```json
    {
        "post_title": "Document Title",
        "note_title": "User1",
        "content": <yaml str> | <str>
        "medias": <list[str]>,
        "metadata": <dict[str,str]>"
    }
    ```

    ## 200 response:
    ```json
    {
        "success": true,
        "message": "<note_title> commented on the document <post_title>"
    }
    ```

    ## Error response:
    ```json
    {"error": "<error message>"}
    ```
    """
    response.headers['Content-Type'] = 'application/json'

    try:
        data = request.json
        required = ["post_title", "note_title", "content"]

        if not data or not all(k in data for k in required):
            response.status = 400
            return json.dumps({"error": "Missing required fields '[post_title, note_title, content]'"})
        
        post_title = data["post_title"]
        note_title = data["note_title"]
        content = data["content"]
        metadatas = data.get("metadata", False)

        if metadatas:
            yaml_metas = oyaml.safe_dump(metadatas)
            content = f"{yaml_metas}\n###\n\n{content}"

        globals.database.write_comment(
            post_title = post_title, 
            note_title = note_title, 
            content = content, 
            medias = data.get("medias", [])
        )

        return json.dumps({"message": f"{note_title} commented on the document {post_title}"})
    
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})


@server.post('/api/attribute')
@post_auth_wrapper
def post_attribute() -> str:
    """
    # POST `/api/attribute`

    Registers new attribute values.
    All the attribute values already existing are ignored.
    If the attribute type does not exist, it is created with the new values.
    
    ## Request body:
    ```json
    {
        "attribute": str,       // the attribute name
        "values": list[str]
    }
    ```

    ## 200 response:
    ```json
    {
        "success": true,
        "message": "attribute '<attribute>' registered"
    }
    ```

    ## Error response:
    ```json
    {"error": "<error message>"}
    ```
    """
    response.headers['Content-Type'] = 'application/json'
    try:
        data = request.json

        required = ["attribute", "values"]
        if not data or not all(k in data for k in required):
            response.status = 400
            return json.dumps({"error": "Missing required fields '[attribute, values]'"})
        
        attribute = data["attribute"]
        values = data.get("values", [])

        globals.database.add_attribute_values(attribute, values)

        return json.dumps({"message": f"attribute '{attribute}' registered"})
    
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})

@server.post('/api/compile/catalog')
@post_auth_wrapper
def post_compile_catalog() -> str:
    """
    # POST `/api/compile/catalog`

    Triggers a rebuild of the catalog from all documents.

    ## 200 response:
    ```json
    {
        "success": true,
        "message": "Catalog compiled successfully"
    }
    ```

    ## Error response:
    ```json
    {"error": "<error message>"}
    ```
    """
    response.headers['Content-Type'] = 'application/json'
    try:
        compile_catalog()
        return json.dumps({"success": True, "message": "Catalog compiled successfully"})
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})

@server.post('/api/compile/attribute')
@post_auth_wrapper
def post_compile_attribute() -> str:
    """
    # POST `/api/compile/attribute`

    Triggers a rebuild of an attribute values list from the catalog.

    
    ## Request body:
    ```json
    {
        "attributes": <list[str]>
    }
    ```
    
    ## 200 response:
    ```json
    {
        "success": true,
        "message": "Catalog compiled successfully"
    }
    ```

    ## Error response:
    ```json
    {"error": "<error message>"}
    ```
    """
    data = request.json

    if not ("attributes" in data and isinstance(data["attribute"],list)):
        response.status = 400
        return json.dumps({"error": "Missing required fields '[attributes]' (list[str])"})
        
    response.headers['Content-Type'] = 'application/json'
    try:
        for attribute in data["attributes"]:
            compile_attribute(attribute)
        return json.dumps({"success": True, "message": f"Attribute '{attribute}' compiled successfully"})
    except Exception as e:
        response.status = 500
        return json.dumps({"error": str(e)})

@server.post('/api/query')
@stream_auth_wrapper
def stream():
    """
    # POST `/api/query`

    Streams a response from the LLM for a given prompt.

    The history is a list of entry containing the role and content of messages.

    Example:
    ```json
    [
        {
            "role": "user",
            "content": "Why is the sky blue?"
        },
        {
            "role": "assistant",
            "content": "The sky is blue because of the way the Earth's atmosphere scatters sunlight."
        },
        ...
    ]
    ```

    ## Request body:
    ```json
    {
        "prompt": <str>,
        "history": <list[dict[str,str]]> (default None)
        "metadata": <bool> (default: true) // whether to include retrieved documents metadata in the response
    }
    ```

    ## Streamed response:
    ```
    <LLM response chunks>
    ```
    """
    
    prompt = request.json.get('prompt', '')
    history = request.json.get('history', None)
    include_metadata = request.json.get('metadata', False)

    if not prompt:
        response.status = 400
        return json.dumps({"error": "Missing required field 'prompt'"})
    
    stream = query(prompt,history,include_metadata)

    response.headers['Content-Type'] = 'text/event-stream'
    
    if include_metadata:
        yield f"{"#METADATA#"}{json.dumps(stream.metadatas)}"

    for chunk in stream:
        if chunk:
            yield chunk


__all__ = [
    'server',
    'get_docs',
    'get_catalog', 
    'get_document_by_name', 
    'get_notes_for_post',
    'get_attributes',
    'post_post',
    'post_comment',
    'post_attribute',
    'stream',
    'post_auth_check',
    'stream_auth_check'
]

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8080)