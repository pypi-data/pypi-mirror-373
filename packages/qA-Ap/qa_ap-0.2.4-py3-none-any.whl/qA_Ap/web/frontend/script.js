window.onBoot = [];

window.Boot = function(){
    window.onBoot.forEach(fn => {
        fn();
    });
};

bootscreen = document.getElementById("bootscreen");
bootface = document.querySelector("#bootscreen .qpface");

window.onBoot.push(()=>{
    setTimeout(()=>{
        bootface.classList.add("open");
        setTimeout(()=>{
            bootscreen.classList.add("fade");
            setTimeout(()=>{
                bootscreen.remove()
            },1000)
        },1000)
    },1000)
});

// ===============================================================================================

// Main application class
class QAAPApp {
    constructor() {
        this.qaap = new QAAP();
        this.catalog = []; // Store the full catalog in memory
        this.filteredDocuments = []; // Store filtered documents

        try{
            const ih = localStorage.getItem("inputHistory");
            if(ih != null){
                let data = JSON.parse(ih);
                data = new Set(data)
                data = Array.from(data)
                this.inputHistory = data;
            }
        }catch(err){
            console.log("Error while loading inputHistory",err);
            this.inputHistory = [];
        }

        this.inputHistoryIndex = 0;
        this.initElements();
        this.initEventListeners();
        this.loadCatalog();
    }

    initElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chat-messages');
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatInput = document.getElementById('chat-input');

        // Document elements
        this.documentsGrid = document.getElementById('documents-grid');
        this.filterContainer = document.getElementById('filter-container');
        this.removeFilters = document.getElementById('remove-filters');

        // Templates
        this.userMessageTemplate = document.getElementById('user-message-template');
        this.llmMessageTemplate = document.getElementById('llm-message-template');
        this.documentTemplate = document.getElementById('document-template');
        this.documentAttributeTemplate = document.getElementById('document-attribute');
        this.filterTemplate = document.getElementById('filter');
        this.externalLinkTemplate = document.getElementById('document-link');

        // Document modal
        this.documentModal = document.getElementById('document-modal');

        // Boot screen
        this.bootScreen = document.getElementById('bootscreen');
    }

    initEventListeners() {
        // Chat input focus handling
        this.messageInput.addEventListener('focus', () => {
            this.chatInput.classList.add('focus');
        });

        this.messageInput.addEventListener('blur', () => {
            this.chatInput.classList.remove('focus');
        });

        
        // Document title click
        this.chatMessages.addEventListener('click', (e) => {
            if (e.target.classList.contains('response-document')) {
                this.handleDocumentTitleClick(e.target);
            }
        });

        this.messageInput.addEventListener('keydown', (ev) => {
            if(ev.key == "ArrowUp"){
                if(this.inputHistory.length > 0 && (this.inputHistoryIndex < this.inputHistory.length)){
                    if(this.inputHistoryIndex == 0){
                        const currentInput = this.messageInput.value.trim();
                        if(currentInput != ""){
                            this.inputHistory.splice(1,0,currentInput);
                        }
                    }
                    this.messageInput.value = this.inputHistory[this.inputHistoryIndex];
                    this.inputHistoryIndex += 1;
                }
            }else if(ev.key == "ArrowDown"){
                this.inputHistoryIndex -= 1
                if(this.inputHistoryIndex == -1){
                    this.inputHistoryIndex = 0;
                    this.messageInput.value = "";
                }else if(this.inputHistory.length > 0){
                    this.messageInput.value = this.inputHistory[this.inputHistoryIndex];
                }
            }else if(ev.key == "ArrowLeft" || ev.key == "ArrowRight"){
            }else{
                this.inputHistoryIndex = 0
            }
        });

        // Send button click
        this.sendButton.addEventListener('click', () => this.handleSendMessage());

        // Enter key in message input
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSendMessage();
            }
        });

        // Remove filters click
        this.removeFilters.addEventListener('click', () => this.clearFilters());

        // Document title click
        this.documentsGrid.addEventListener('click', (e) => {
            if (e.target.classList.contains('document-title')) {
                this.handleDocumentTitleClick(e.target);
            }
        });

        // Filter click
        this.filterContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-name')) {
                this.handleFilterClick(e.target);
            } else if (e.target.classList.contains('close-filter')) {
                this.handleRemoveFilter(e.target);
            }
        });

        // Document attribute click
        this.documentsGrid.addEventListener('click', (e) => {
            if (e.target.classList.contains('document-attribute')) {
                this.handleAttributeClick(e.target);
            }
        });

        // External link click
        this.documentsGrid.addEventListener('click', (e) => {
            if (e.target.classList.contains('external-link')) {
                this.handleExternalLinkClick(e.target);
            }
        });

                
        // Document modal close button
        this.documentModal.querySelector('.close').addEventListener('click', () => {
            this.documentModal.classList.add('closed');
        });

        // Load document content button
        document.getElementById('load-document-content').addEventListener('click', async (e) => {
            const title = document.querySelector('.document-modal-title').textContent;
            await this.loadDocumentContent(title);
        });

        // Load document notes button
        document.getElementById('load-document-notes').addEventListener('click', async (e) => {
            const title = document.querySelector('.document-modal-title').textContent;
            await this.loadDocumentComments(title);
        });

        // Close modal when clicking outside the content
        this.documentModal.addEventListener('click', (e) => {
            if (e.target === this.documentModal) {
                this.documentModal.classList.add('closed');
            }
        });

        window.addEventListener("unload",()=>{
            try{
                const data = JSON.stringify(this.inputHistory);
                localStorage.setItem("inputHistory", data);
            }catch{}
        })

    }

    async loadCatalog() {
        try {
            this.catalog = await this.qaap.getCatalog();
            this.filteredDocuments = [...this.catalog]; // Initialize filtered documents
            this.renderDocuments(this.filteredDocuments);

            window.Boot();
        } catch (error) {
            console.error('Error loading catalog:', error);
            this.addSystemMessage('Failed to load documents. Please try again later.');
        }
    }

    renderDocuments(documents) {
        this.documentsGrid.innerHTML = '';

        documents.forEach(doc => {
            const docElement = this.createDocumentElement(doc);
            this.documentsGrid.appendChild(docElement);
        });
    }

    createDocumentElement(doc) {
        const template = this.documentTemplate.content.cloneNode(true);
        const element = template.querySelector('.document');

        // Set title
        const titleElement = element.querySelector('.document-title');
        titleElement.textContent = doc.title;

        // Set description
        const descriptionElement = element.querySelector('.document-description');
        descriptionElement.textContent = doc.content || 'No description available';

        // Set icon
        const iconElement = element.querySelector('.document-icon img');
        iconElement.src = doc.metadatas.icon
            ? doc.metadatas.icon
            : 'static/icon.png';
        iconElement.alt = `${doc.title} icon`;

        // Add attributes
        const attributesContainer = element.querySelector('.document-attributes');
        if (doc.metadatas.tags && doc.metadatas.tags.length > 0) {
            doc.metadatas.tags.forEach(tag => {
                const attrElement = this.createAttributeElement(tag);
                attributesContainer.appendChild(attrElement);
            });
        }

        // Add external link if available
        if (doc.metadatas.links && doc.metadatas.links.length > 0) {
            const linkElement = this.createExternalLinkElement(doc.metadatas.links[0]);
            titleElement.insertAdjacentElement("beforebegin",linkElement);
        }

        return element;
    }

    createAttributeElement(attributeName) {
        const template = this.documentAttributeTemplate.content.cloneNode(true);
        const element = template.querySelector('.document-attribute');
        element.textContent = attributeName;
        return element;
    }

    createExternalLinkElement(link) {
        const template = this.externalLinkTemplate.content.cloneNode(true);
        const element = template.querySelector('a');
        element.href = link;
        element.target = '_blank';
        element.rel = 'noopener noreferrer';
        return element;
    }

    createFilterElement(filterName) {
        const template = this.filterTemplate.content.cloneNode(true);
        const element = template.querySelector('.filter');
        element.querySelector('.filter-name').textContent = filterName;
        return element;
    }

    handleSendMessage() {
        const message = this.messageInput.value.trim();
        if(this.inputHistoryIndex == 0){
            this.inputHistory.unshift(message);
        }
        if (message) {
            this.addUserMessage(message);
            this.processQuery(message);
            this.messageInput.value = '';
        }
    }

    addUserMessage(message) {
        const template = this.userMessageTemplate.content.cloneNode(true);
        const element = template.querySelector('.chat-message');
        element.querySelector('p').textContent = message;
        this.chatMessages.appendChild(element);
        this.scrollToBottom();
    }

    addSystemMessage(message) {
        const template = this.llmMessageTemplate.content.cloneNode(true);
        const element = template.querySelector('.chat-message');
        element.querySelector('p').textContent = message;
        this.chatMessages.appendChild(element);
        this.scrollToBottom();
        return element;
    }

    displayResponseDocuments(llmMessage,documents){
        const target = llmMessage.querySelector(".message-documents");
        documents.forEach(doc=>{
            const link = document.createElement("span");
            link.classList.add("response-document");
            link.textContent = doc.replaceAll(/\[|\]/g,"");
            target.appendChild(link);
        });
    }

    async processQuery(query) {
        try {
            let msg = this.addSystemMessage('');
            let txt = msg.querySelector('p');

            let metadata = null;

            let responseDocs = [];

            let callback = (chunk, metadata) => {
                if(chunk == "DONE"){
                    txt.textContent = txt.textContent.replaceAll(/\[(.+)\]/g,(_,group)=>{
                        responseDocs = group.split(",");
                        responseDocs = responseDocs.map(doc=>{
                            return doc.replace(/.+\s*\d*\s*-\s*/,"");
                        });
                        return "";
                    });
                    if(responseDocs)
                        this.displayResponseDocuments(msg,responseDocs);
                }else if (metadata) {
                    metadata = metadata;
                } else {
                    txt.textContent += chunk;
                }
            }

            // Get the chat history (last 10 messages)
            const chatHistory = this.getChatHistory();

            // Call the real query method from QAAP with the query and history
            const results = await this.qaap.query(query, callback, chatHistory, true);

        } catch (error) {
            console.error('Error processing query:', error);
            this.addSystemMessage('An error occurred while processing your query. Please try again.');
        }
    }

    // Helper method to get chat history (last 10 messages)
    getChatHistory() {
        const messages = Array.from(this.chatMessages.querySelectorAll('.chat-message'));
        const history = [];

        // Get the last 10 messages
        const startIndex = Math.max(0, messages.length - 10);

        for (let i = startIndex; i < messages.length; i++) {
            const message = messages[i];
            const role = message.classList.contains('user-message') ? 'user' : 'assistant';
            const content = message.querySelector('p').textContent;

            history.push({ role:role, content:content });
        }

        return history;
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    _isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (err) {
            return false;
        }
    }

    handleDocumentTitleClick(titleElement) {
        const title = titleElement.textContent;
        const doc = this.filteredDocuments.find(d => d.title === title);

        if (doc) {
            const modal = document.getElementById('document-modal');
            const modalTitle = modal.querySelector('.document-modal-title');
            const modalIcon = modal.querySelector('.document-modal-icon img');
            const modalText = modal.querySelector('.document-modal-text');
            const modalMetadata = modal.querySelector('.document-modal-metadata ul');
            const commentsContainer = modal.querySelector('.document-modal-notes');
            const loadButton = document.getElementById('load-document-content');
            loadButton.style.display = "block";

            // Set modal content
            modalTitle.textContent = doc.title;
            modalIcon.src = doc.metadatas.icon || 'static/icon.png';
            modalText.textContent = doc.content || 'No content available';

            // Clear and populate metadata
            modalMetadata.innerHTML = '';
            for (let [key, value] of Object.entries(doc.metadatas)) {
                if (key !== 'icon' && key !== 'notes') {
                    const li = document.createElement('li');
                    value = value.map(val=>{
                        if(this._isValidUrl(val) == true){
                            return `<a href="${val}" target="_blank">${val}</a>`;
                        }else{
                            return val;
                        }
                    })
                    li.innerHTML = `<strong>${key}:</strong> ${value.join(", ")}`;
                    modalMetadata.appendChild(li);
                }
            }

            // Clear notes container
            commentsContainer.innerHTML = `
                <button id="load-document-notes">Charger les commentaires</button>
            `;

            // Reattach event listener for notes button
            commentsContainer.querySelector('#load-document-notes').addEventListener('click', async () => {
                await this.loadDocumentComments(doc.title);
            });
            
            // Open the modal
            modal.classList.remove('closed');
        }
    }

    async loadDocumentContent(title) {
        try {
            const document = await this.qaap.getPostByName(title);
            const modalText = document.querySelector('.document-modal-text');
            modalText.textContent = document.content || 'No content available';

            // Replace the load button with a message
            const loadButton = document.getElementById('load-document-content');
            loadButton.style.display = "none";
            // if (loadButton) {
            //     loadButton.replaceWith(document.createElement('p').textContent = 'Contenu chargé');
            // }
        } catch (error) {
            console.error('Error loading document content:', error);
            const modalText = document.querySelector('.document-modal-text');
            modalText.textContent = 'Failed to load document content. Please try again.';
        }
    }

    async loadDocumentComments(title) {
        try {
            const notes = await this.qaap.getCommentsForPost(title);
            const commentsContainer = document.querySelector('.document-modal-notes');

            // Clear previous notes
            commentsContainer.innerHTML = '';

            if (notes.length === 0) {
                commentsContainer.innerHTML = '<p>Aucun commentaire trouvé.</p>';
                return;
            }

            // Create note elements
            notes.forEach(note => {
                const commentElement = this.createCommentElement(note);
                commentsContainer.appendChild(commentElement);
            });

        } catch (error) {
            console.error('Error loading document notes:', error);
            const commentsContainer = document.querySelector('.document-modal-notes');
            commentsContainer.innerHTML = '<p>Failed to load notes. Please try again.</p>';
        }
    }

    createCommentElement(note) {
        const template = document.getElementById('document-modal-note').content.cloneNode(true);
        const element = template.querySelector('.document-modal-note');

        // Set note content
        const titleElement = element.querySelector('.document-note-title');
        titleElement.textContent = note.note_title || 'Anonymous';

        const descriptionElement = element.querySelector('.document-note-description');
        descriptionElement.textContent = note.content || 'No note content';

        // Add metadata if available
        if (note.metadata) {
            const metadataElement = document.createElement('div');
            metadataElement.className = 'document-note-metadata';

            for (let [key, value] of Object.entries(note.metadata)) {
                const metaItem = document.createElement('p');
                metaItem.innerHTML = `<strong>${key}:</strong> ${value}`;
                metadataElement.appendChild(metaItem);
            }

            element.appendChild(metadataElement);
        }

        return element;
    }

    handleExternalLinkClick(linkElement) {
        const url = linkElement.href;
        window.open(url, '_blank');
    }

    handleAttributeClick(attributeElement) {
        const attribute = attributeElement.textContent;
        this.addFilter(attribute);
    }

    addFilter(filterName) {
        // Check if filter already exists
        const existingFilters = Array.from(this.filterContainer.querySelectorAll('.filter-name'));
        if (existingFilters.some(filter => filter.textContent === filterName)) {
            return;
        }

        const filterElement = this.createFilterElement(filterName);
        this.filterContainer.appendChild(filterElement);

        // Apply the filter to documents
        this.applyFilters();
    }

    handleFilterClick(filterElement) {
        filterElement.parentElement.remove();
        this.applyFilters();
    }

    handleRemoveFilter(closeButton) {
        const filterElement = closeButton.closest('.filter');
        if (filterElement) {
            filterElement.remove();
            this.applyFilters();
        }
    }

    clearFilters() {
        this.filterContainer.innerHTML = '';
        this.applyFilters();
    }

    applyFilters() {
        const filters = Array.from(this.filterContainer.querySelectorAll('.filter-name'))
            .map(filter => filter.textContent.toLowerCase());

        if (filters.length === 0) {
            // If no filters, show all documents
            this.filteredDocuments = [...this.catalog];
        } else {
            // Filter documents based on active filters
            this.filteredDocuments = this.catalog.filter(doc => {
                if (!doc.metadatas.tags) return false;
                return filters.every(filter =>
                    doc.metadatas.tags.some(tag => tag.toLowerCase().includes(filter))
                );
            });
        }

        this.renderDocuments(this.filteredDocuments);
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new QAAPApp();
});