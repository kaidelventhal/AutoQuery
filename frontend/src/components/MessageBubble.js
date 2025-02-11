import React from 'react';
import { Box, Text, Code } from '@chakra-ui/react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';

function MessageBubble({ message }) {
  const isUser = message.type === 'user';

  return (
    <Box
      alignSelf={isUser ? 'flex-end' : 'flex-start'}
      maxW="70%"
      bg={isUser ? 'brand.500' : 'white'}
      color={isUser ? 'white' : 'gray.800'}
      p={4}
      borderRadius="lg"
      boxShadow="sm"
    >
      {message.content.includes('```sql') ? (
        <>
          <Text mb={2}>{message.content.split('```sql')[0]}</Text>
          <SyntaxHighlighter
            language="sql"
            style={tomorrow}
            customStyle={{
              borderRadius: '4px',
              fontSize: '14px'
            }}
          >
            {message.content.split('```sql')[1].split('```')[0]}
          </SyntaxHighlighter>
          <Text mt={2}>{message.content.split('```')[2]}</Text>
        </>
      ) : (
        <Text>{message.content}</Text>
      )}
      <Text
        fontSize="xs"
        color={isUser ? 'whiteAlpha.700' : 'gray.500'}
        mt={1}
      >
        {new Date(message.timestamp).toLocaleTimeString()}
      </Text>
    </Box>
  );
}

export default MessageBubble;