document.addEventListener('DOMContentLoaded', () => {
    const messageList = document.getElementById('message-list');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorDisplay = document.getElementById('error-display');

    // --- Configuration ---
    // IMPORTANT: After deploying the backend service, update this URL!
    // Get the backend service URL from `gcloud app deploy backend/app.yaml` output
    // (e.g., https://backend-dot-your-project-id.appspot.com)
    // and append '/api/chat' to it.
    const API_URL = 'https://backend-dot-autoquery-454320.uc.r.appspot.com/api/chat'; // <<< UPDATE THIS AFTER BACKEND DEPLOYMENT
    // Example Deployed URL: const API_URL = 'https://backend-dot-your-project-id.appspot.com/api/chat';

    // In-memory chat history (client-side only for display)
    // Note: The actual history context for the LLM is managed server-side in app.py
    let chatHistory = [
        { sender: 'agent', message: 'Welcome to AutoQuery AI! How can I help you find vehicle data today?' }
    ];

    // --- Functions ---

    /** Renders messages from chatHistory to the DOM */
    function renderMessages() {
        messageList.innerHTML = ''; // Clear existing messages
        chatHistory.forEach(msg => {
            const listItem = document.createElement('li');
            listItem.classList.add('message');
            listItem.classList.add(msg.sender === 'user' ? 'user-message' : 'agent-message');

            // Sanitize output - Use textContent to prevent XSS
            listItem.textContent = msg.message;

            messageList.appendChild(listItem);
        });
        // Scroll to the bottom
        // Use setTimeout to allow the DOM to update before scrolling
        setTimeout(() => {
             messageList.scrollTop = messageList.scrollHeight;
        }, 0);
    }

    /** Displays error messages */
    function displayError(errorMessage) {
        errorDisplay.textContent = `Error: ${errorMessage}`;
        errorDisplay.style.display = 'block';
        loadingIndicator.style.display = 'none'; // Hide loading if error occurs
    }

    /** Hides the error display */
    function clearError() {
        errorDisplay.textContent = '';
        errorDisplay.style.display = 'none';
    }

    /** Sends message to backend API */
    async function sendMessageToApi(userMessage) {
        loadingIndicator.style.display = 'block';
        clearError();
        setInteractionState(true); // Disable input

        // Add user message to display history immediately
        chatHistory.push({ sender: 'user', message: userMessage });
        renderMessages();
        messageInput.value = ''; // Clear input field


        // Note: We are NOT sending the client-side history here.
        // The backend maintains its own history per instance.
        // If you needed persistent history across requests, the backend
        // would need to load/save it, and the API call might include a session ID.
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    // Not sending history from client: history: historyForApi,
                }),
            });

            if (!response.ok) {
                let errorMsg = `Request failed (${response.status})`;
                try {
                    // Try to get more specific error from backend response
                    const errorData = await response.json();
                    errorMsg = errorData.error || errorMsg;
                } catch (e) { /* Ignore if no JSON body or parsing error */ }
                throw new Error(errorMsg);
            }

            const data = await response.json();

            // Add agent response to history and re-render
            chatHistory.push({ sender: 'agent', message: data.response || "Received empty response." });
            renderMessages();

        } catch (error) {
            console.error('API Error:', error);
            displayError(error.message || 'Could not connect to the agent.');
            // Optional: Remove the user's message from display if API call failed?
            // chatHistory.pop(); // Removes the last added message (the user's)
            // renderMessages();
        } finally {
            loadingIndicator.style.display = 'none';
            setInteractionState(false); // Re-enable input
        }
    }

    /** Enables/Disables input field and send button */
    function setInteractionState(disabled) {
        messageInput.disabled = disabled;
        sendButton.disabled = disabled;
        // Optionally change styles for disabled state
        messageInput.style.cursor = disabled ? 'not-allowed' : '';
        sendButton.style.cursor = disabled ? 'not-allowed' : 'pointer';
    }


    // --- Event Listeners ---

    chatForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent page reload
        const userMessage = messageInput.value.trim();

        if (userMessage && !sendButton.disabled) { // Check if input is not disabled
            // Send message to backend (which also handles rendering user message)
            sendMessageToApi(userMessage);
        }
    });

    // --- Initial Render ---
    renderMessages();

}); // End DOMContentLoaded