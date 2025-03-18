import React from 'react';
import ReactMarkdown from 'react-markdown';

const MessageList = ({ history }) => {
  return (
    <div className="message-list">
      {history.map((msg, index) => (
        <div key={index} className={`message ${msg.sender}`}>
          <strong>{msg.sender === 'user' ? 'You' : 'Agent'}:</strong>
          {msg.sender === 'agent' ? (
            <ReactMarkdown>{msg.message}</ReactMarkdown>
          ) : (
            <span>{msg.message}</span>
          )}
        </div>
      ))}
    </div>
  );
};

export default MessageList;
