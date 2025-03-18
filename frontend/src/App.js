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
      <header>
         <h1>AutoQuerry</h1>
         <h2>Automotive Market Research</h2>
      </header>
      <MessageList history={history} />
      <ChatInput 
        onSend={(msg) => addMessage(msg, 'user')}
        addMessage={addMessage}
        history={history}
      />
      <footer>
        <p>Created by Kai Delventhal</p>
      </footer>
    </div>
  );
}

export default App;
