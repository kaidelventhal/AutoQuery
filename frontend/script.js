document.addEventListener('DOMContentLoaded', () => {
    const messageList = document.getElementById('message-list');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorDisplay = document.getElementById('error-display');

    // --- Configuration ---
    // Define API URL (could be read from meta tag or config object if needed later)
    const API_URL = 'http://localhost:5000/api/chat'; // Use relative path if served by same App Engine app potentially,
                               // or set full URL if backend is separate service:
                               // const API_URL = 'YOUR_BACKEND_DEPLOYED_URL/api/chat';

    // In-memory chat history
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

            // Use textContent to prevent potential XSS from agent response if it contained HTML
            // If markdown is NEEDED, a library like 'marked' or 'showdown' could be added,
            // but for simplicity, we'll render as text.
            listItem.textContent = msg.message;

            messageList.appendChild(listItem);
        });
        // Scroll to the bottom
        messageList.scrollTop = messageList.scrollHeight;
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

        // Prepare history for API (simple array of objects)
        const historyForApi = chatHistory.map(h => ({
            sender: h.sender,
            message: h.message
        }));

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    history: historyForApi, // Send current history
                }),
            });

            if (!response.ok) {
                 let errorMsg = `Request failed (${response.status})`;
                 try {
                     const errorData = await response.json();
                     errorMsg = errorData.error || errorMsg;
                 } catch (e) { /* Ignore if no JSON body */ }
                 throw new Error(errorMsg);
            }

            const data = await response.json();

            // Add agent response to history and re-render
            chatHistory.push({ sender: 'agent', message: data.response || "Received empty response." });
            renderMessages();

        } catch (error) {
            console.error('API Error:', error);
            displayError(error.message || 'Could not connect to the agent.');
            // Optional: remove the user's message if API call failed?
        } finally {
             loadingIndicator.style.display = 'none';
             setInteractionState(false); // Re-enable input
        }
    }

    /** Enables/Disables input field and send button */
    function setInteractionState(disabled) {
         messageInput.disabled = disabled;
         sendButton.disabled = disabled;
    }


    // --- Event Listeners ---

    chatForm.addEventListener('submit', (event) => {
        event.preventDefault(); // Prevent page reload
        const userMessage = messageInput.value.trim();

        if (userMessage) {
            // Add user message to history and render
            chatHistory.push({ sender: 'user', message: userMessage });
            renderMessages();
            messageInput.value = ''; // Clear input field

            // Send message to backend
            sendMessageToApi(userMessage);
        }
    });

    // --- Initial Render ---
    renderMessages();

}); // End DOMContentLoaded