import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#00D9FF', light: '#5CEFFF', dark: '#00A0CC' },
    secondary: { main: '#FF6584', light: '#FF8FA3', dark: '#D44A64' },
    background: {
      default: '#0A0E1A',
      paper: '#111827',
    },
    success: { main: '#34D399' },
    warning: { main: '#FBBF24' },
    error: { main: '#F87171' },
    text: {
      primary: '#F0F4F8',
      secondary: '#94A3B8',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 700 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(0, 217, 255, 0.1)',
          transition: 'border-color 0.3s, box-shadow 0.3s',
          '&:hover': {
            borderColor: 'rgba(0, 217, 255, 0.25)',
            boxShadow: '0 0 24px rgba(0, 217, 255, 0.06)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600 },
        containedPrimary: {
          background: 'linear-gradient(135deg, #00D9FF 0%, #5CEFFF 100%)',
          color: '#0A0E1A',
          '&:hover': {
            background: 'linear-gradient(135deg, #00A0CC 0%, #00D9FF 100%)',
          },
        },
      },
    },
  },
});

export default theme;
