import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Flex,
  Input,
  IconButton,
  VStack,
  Text,
  useToast
} from '@chakra-ui/react';
import { SendIcon } from '@chakra-ui/icons';
import MessageBubble from './MessageBubble';
import axios from 'axios';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const endMessageRef = useRef(null);
  const toast = useToast();

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = {
      type: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, newMessage]);
    setInput('');

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        message: input,
        history: messages
      });

      setMessages(prev => [...prev, {
        type: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp
      }]);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to get response',
        status: 'error',
        duration: 3000
      });
    }
  };

  useEffect(() => {
    endMessageRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <Box gridColumn={{ base: '1', lg: '2' }} p={4} height="calc(100vh - 60px)">
      <Flex direction="column" h="100%">
        <VStack flex="1" overflowY="auto" spacing={4} mb={4}>
          {messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg} />
          ))}
          <div ref={endMessageRef} />
        </VStack>
        <Flex>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about any vehicle..."
            mr={2}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          />
          <IconButton
            icon={<SendIcon />}
            onClick={sendMessage}
            colorScheme="brand"
            aria-label="Send message"
          />
        </Flex>
      </Flex>
    </Box>
  );
}

export default ChatInterface;