import React from 'react';
import { ChakraProvider, Box, Grid } from '@chakra-ui/react';
import { theme } from './theme';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';

function App() {
  return (
    <ChakraProvider theme={theme}>
      <Box minH="100vh" bg="gray.50">
        <Grid
          templateColumns={{ base: '1fr', lg: '280px 1fr' }}
          templateRows="60px 1fr"
        >
          <Header />
          <Sidebar />
          <ChatInterface />
        </Grid>
      </Box>
    </ChakraProvider>
  );
}

export default App;