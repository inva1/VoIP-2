import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import theme from './theme';
import { AuthProvider } from './context/AuthContext';
import UserLayout from './components/layout/UserLayout';
import Login from './pages/Login';
import Register from './pages/Register';
import Overview from './pages/Overview';
import Subscription from './pages/Subscription';
import DIDManager from './pages/DIDManager';
import KYCSubmit from './pages/KYCSubmit';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route element={<UserLayout />}>
              <Route path="/" element={<Overview />} />
              <Route path="/subscription" element={<Subscription />} />
              <Route path="/numbers" element={<DIDManager />} />
              <Route path="/kyc" element={<KYCSubmit />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
