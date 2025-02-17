import React, { useState } from 'react';
import ChatInput from './ChatInput';
import MessageList from './MessageList';
import './App.css';

function App() {
  const [history, setHistory] = useState([]);
  
  const addMessage = (message, sender = 'user') => {
    setHistory(prevHistory => [...prevHistory, { sender, message }]);
  };

  return (
    <div className="App">
      <h1>Chat Interface</h1>
      <MessageList history={history} />
      <ChatInput onSend={(msg) => addMessage(msg, 'user')} addMessage={addMessage} history={history} />
    </div>
  );
}

export default App;
