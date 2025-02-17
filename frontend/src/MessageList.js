import React from 'react';

const MessageList = ({ history }) => {
  return (
    <div className="message-list">
      {history.map((msg, index) => (
        <div key={index} className={`message ${msg.sender}`}>
          <strong>{msg.sender === 'user' ? 'You' : 'Agent'}:</strong> {msg.message}
        </div>
      ))}
    </div>
  );
};

export default MessageList;
