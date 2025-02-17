import React, { useState } from 'react';

const ChatInput = ({ onSend, addMessage, history }) => {
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Append user message locally
    onSend(input);

    // Call the Flask API
    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          history: history.map(h => h.message)
        })
      });
      const data = await response.json();
      // Append agent's response
      addMessage(data.response, 'agent');
    } catch (error) {
      console.error("Error sending message:", error);
    }
    setInput('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') sendMessage();
  };

  return (
    <div className="chat-input">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
};

export default ChatInput;
