import React, { useState } from 'react';
import { useNavigate, Navigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Box, Card, CardContent, TextField, Button, Typography, Alert, CircularProgress,
} from '@mui/material';
import PhoneInTalkIcon from '@mui/icons-material/PhoneInTalk';

export default function Login() {
  const { user, loading, login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (loading) return null;
  if (user) return <Navigate to="/" replace />;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Login failed');
    }
    setSubmitting(false);
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(ellipse at top, #111827 0%, #0A0E1A 70%)' }}>
      <Card sx={{ width: 400, maxWidth: '90vw' }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box sx={{
              width: 56, height: 56, borderRadius: '50%', mx: 'auto', mb: 2,
              background: 'linear-gradient(135deg, #00D9FF, #34D399)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <PhoneInTalkIcon sx={{ color: '#0A0E1A', fontSize: 28 }} />
            </Box>
            <Typography variant="h5" fontWeight={700}>Sign In</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Access your VoIP account
            </Typography>
          </Box>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <form onSubmit={handleSubmit}>
            <TextField fullWidth label="Email" type="email" value={email}
              onChange={(e) => setEmail(e.target.value)} margin="normal" required autoFocus id="user-login-email" />
            <TextField fullWidth label="Password" type="password" value={password}
              onChange={(e) => setPassword(e.target.value)} margin="normal" required id="user-login-password" />
            <Button fullWidth type="submit" variant="contained" size="large"
              disabled={submitting} sx={{ mt: 3, py: 1.5 }} id="user-login-submit">
              {submitting ? <CircularProgress size={24} color="inherit" /> : 'Sign In'}
            </Button>
          </form>
          <Typography variant="body2" align="center" sx={{ mt: 2 }} color="text.secondary">
            Don't have an account? <Link to="/register" style={{ color: '#00D9FF' }}>Register</Link>
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
