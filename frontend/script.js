document.addEventListener('DOMContentLoaded', () => {
    const messageList = document.getElementById('message-list');
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorDisplay = document.getElementById('error-display');
    const agentStepsContainer = document.getElementById('agent-steps-display');
    const agentStepsCode = document.getElementById('agent-steps-code');

    const API_URL = 'https://backend-dot-autoquery-472902.ue.r.appspot.com/api/chat';

    let chatHistory = [
        { sender: 'agent', message: 'Welcome to AutoQuery! How can I help you find vehicle data today?' }
    ];

    function renderMessages() {
        messageList.innerHTML = '';
        chatHistory.forEach(msg => {
            const listItem = document.createElement('li');
            listItem.classList.add('message', msg.sender === 'user' ? 'user-message' : 'agent-message');
            listItem.textContent = msg.message;
            messageList.appendChild(listItem);
        });
        setTimeout(() => { messageList.scrollTop = messageList.scrollHeight; }, 0);
    }

    function displayError(errorMessage) {
        errorDisplay.textContent = `Error: ${errorMessage}`;
        errorDisplay.style.display = 'block';
    }

    function setInteractionState(disabled) {
        messageInput.disabled = disabled;
        sendButton.disabled = disabled;
    }

    async function sendMessageToApi(userMessage) {
        loadingIndicator.style.display = 'block';
        errorDisplay.style.display = 'none';
        agentStepsContainer.style.display = 'none';
        setInteractionState(true);

        chatHistory.push({ sender: 'user', message: userMessage });
        renderMessages();
        messageInput.value = '';

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Request failed (${response.status})`);
            }

            const data = await response.json();
            
            if (data.agent_steps) {
                agentStepsCode.textContent = data.agent_steps;
                agentStepsContainer.style.display = 'block';
            }

            const agentMessage = data.final_response || "Received an empty response.";
            chatHistory.push({ sender: 'agent', message: agentMessage });
            renderMessages();

        } catch (error) {
            console.error('API Error:', error);
            displayError(error.message);
        } finally {
            loadingIndicator.style.display = 'none';
            setInteractionState(false);
        }
    }

    chatForm.addEventListener('submit', (event) => {
        event.preventDefault();
        const userMessage = messageInput.value.trim();
        if (userMessage && !sendButton.disabled) {
            sendMessageToApi(userMessage);
        }
    });

    renderMessages();
});