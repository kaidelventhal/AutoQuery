import { extendTheme } from '@chakra-ui/react';

export const theme = extendTheme({
  colors: {
    brand: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      500: '#0284c7',
      600: '#0369a1',
      700: '#075985',
    },
    automotive: {
      red: '#dc2626',
      silver: '#737373',
      blue: '#2563eb',
    }
  },
  components: {
    Button: {
      variants: {
        solid: {
          bg: 'brand.500',
          color: 'white',
          _hover: {
            bg: 'brand.600',
          }
        }
      }
    }
  }
});