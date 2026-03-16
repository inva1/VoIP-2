import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6C63FF', light: '#9D97FF', dark: '#4A42D4' },
    secondary: { main: '#FF6584', light: '#FF8FA3', dark: '#D44A64' },
    background: {
      default: '#0B0E1A',
      paper: '#131729',
    },
    success: { main: '#2DD4BF' },
    warning: { main: '#FBBF24' },
    error: { main: '#F87171' },
    text: {
      primary: '#E8EAED',
      secondary: '#9AA0A6',
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
          border: '1px solid rgba(108, 99, 255, 0.12)',
          transition: 'border-color 0.3s, box-shadow 0.3s',
          '&:hover': {
            borderColor: 'rgba(108, 99, 255, 0.3)',
            boxShadow: '0 0 20px rgba(108, 99, 255, 0.08)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600 },
        containedPrimary: {
          background: 'linear-gradient(135deg, #6C63FF 0%, #9D97FF 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #5A52E0 0%, #8B85FF 100%)',
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: { fontWeight: 700, color: '#9AA0A6', textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.08em' },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 600, letterSpacing: '0.02em' },
      },
    },
  },
});

export default theme;
