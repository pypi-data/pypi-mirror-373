/**
 * ****************************************************
 *         qA_Ap - query About Anything package
 * ****************************************************
 * 
 * Frontend API interface for qA_Ap.
 * 
 * Provides methods to interact with the backend API for documents, notes, attributes, catalog, and LLM queries.
 */

class QAAP {
    /**
     * Create a QAAP instance.
     * @param {string} baseUrl - The base URL for the API endpoints.
     */
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    /**
     * Fetches the catalog of documents.
     * @returns {Promise<Object>} The catalog as a JSON object.
     */
    async getCatalog() {
        try {
            const response = await fetch(`${this.baseUrl}/catalog`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching catalog:', error);
            throw error;
        }
    }

    /**
     * Fetches a document by its name.
     * @param {string} name - The name of the document.
     * @returns {Promise<Object>} The document as a JSON object.
     */
    async getPostByName(name) {
        try {
            const response = await fetch(`${this.baseUrl}/document/${encodeURIComponent(name)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching document ${name}:`, error);
            throw error;
        }
    }

    /**
     * Fetches all notes for a given document.
     * @param {string} postTitle - The title of the document.
     * @returns {Promise<Object>} The notes as a JSON array.
     */
    async getCommentsForPost(postTitle) {
        try {
            const response = await fetch(`${this.baseUrl}/notes/${encodeURIComponent(postTitle)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching notes for document ${postTitle}:`, error);
            throw error;
        }
    }

    /**
     * Fetches attributes by attribute name.
     * @param {string} attributeName - The name of the attribute.
     * @returns {Promise<Object>} The attributes as a JSON object.
     */
    async getAttributes(attributeName) {
        try {
            const response = await fetch(`${this.baseUrl}/attributes/${encodeURIComponent(attributeName)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`Error fetching attributes for ${attributeName}:`, error);
            throw error;
        }
    }

    /**
     * Posts a new document to the backend.
     * @param {string} title - The title of the document.
     * @param {string} content - The content of the document.
     * @param {Object|null} metadata - Optional metadata for the document.
     * @param {Array} medias - Optional list of media files (base64 strings).
     * @returns {Promise<Object>} The server response.
     */
    async postPost(title, content, metadata = null, medias = []) {
        try {
            const body = {
                title,
                content,
                medias
            };

            if (metadata) {
                body.metadata = metadata;
            }

            const response = await fetch(`${this.baseUrl}/document`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error posting document:', error);
            throw error;
        }
    }

    /**
     * Posts a new note to a document.
     * @param {string} postTitle - The title of the document.
     * @param {string} note_title - The name of the note_title.
     * @param {string} content - The content of the note.
     * @param {Object|null} metadata - Optional metadata for the note.
     * @param {Array} medias - Optional list of media files (base64 strings).
     * @returns {Promise<Object>} The server response.
     */
    async postComment(postTitle, note_title, content, metadata = null, medias = []) {
        try {
            const body = {
                post_title: postTitle,
                note_title,
                content,
                medias
            };

            if (metadata) {
                body.metadata = metadata;
            }

            const response = await fetch(`${this.baseUrl}/note`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error posting note:', error);
            throw error;
        }
    }

    /**
     * Posts a new attribute to the backend.
     * @param {string} attribute - The attribute name.
     * @param {Array} values - The values for the attribute.
     * @returns {Promise<Object>} The server response.
     */
    async postAttribute(attribute, values) {
        try {
            const response = await fetch(`${this.baseUrl}/attribute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ attribute, values })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Error posting attribute:', error);
            throw error;
        }
    }

    /**
     * Calls the /api/compile/catalog endpoint to trigger a rebuild of the catalog.
     * @returns {Promise<Object>} The server response.
     */
    async compileCatalog() {
        try {
            const response = await fetch(`${this.baseUrl}/compile/catalog`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error compiling catalog:', error);
            throw error;
        }
    }

    /**
     * Calls the /api/compile/attribute endpoint to trigger a rebuild of attribute values.
     * @param {Array<string>} attributes - List of attribute names to compile.
     * @returns {Promise<Object>} The server response.
     */
    async compileAttribute(attributes) {
        try {
            const response = await fetch(`${this.baseUrl}/compile/attribute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ attributes })
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error compiling attribute:', error);
            throw error;
        }
    }
    
    /**
     * Sends a prompt to the backend for LLM querying and streams the response.
     * @param {string} prompt - The prompt/question to send.
     * @param {function} callback - Callback function to handle streamed chunks.
     * @param {Array|null} history - Optional conversation history.
     * @param {boolean} metadata - Whether to request metadata.
     * @returns {Promise<void>}
     */
    async query(prompt, callback, history = null, metadata = false) {
        try {
            const body = {
                prompt,
                metadata
            };

            if (history) {
                body.history = history;
            }

            const response = await fetch(`${this.baseUrl}/query`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
                
            reader.read().then(function pump({ done, value }) {
                
                if (done) {
                    callback("DONE");
                    return;
                }

                let raw = new TextDecoder().decode(value);

                if(typeof raw == "string"){
                    if(raw.startsWith("#METADATA#")){
                        console.log("METAS")
                        let metadatas = JSON.parse(raw.replace("#METADATA#",""));
                        callback("METADATA",metadatas);
                        return reader.read().then(pump);
                    }else{
                        callback(raw);
                        return reader.read().then(pump);
                    }
                }else{
                    callback("");
                    return;
                }
            });
            
        } catch (error) {
            console.error('Error querying:', error);
            throw error;
        }
    }
}