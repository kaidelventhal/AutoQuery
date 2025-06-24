document.addEventListener('DOMContentLoaded', () => {
    const messageList = document.getElementById('message-list');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorDisplay = document.getElementById('error-display');

    const API_URL = 'https://backend-dot-autoquery-new.uc.r.appspot.com/api/chat';

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

            let agentMessage = "";
            // Check if there is a status report to display
            if (data.status && data.status.trim() !== "") {
                agentMessage += "--- Agent Status ---\n";
                agentMessage += data.status;
                agentMessage += "--- Final Answer ---\n";
            }
            
            agentMessage += data.final_response || "Received empty response.";

            // Add the combined message to the chat history
            chatHistory.push({ sender: 'agent', message: agentMessage });
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