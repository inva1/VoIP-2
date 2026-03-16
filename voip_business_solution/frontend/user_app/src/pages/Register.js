import React, { useState } from 'react';
import { useNavigate, Navigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Box, Card, CardContent, TextField, Button, Typography, Alert, CircularProgress,
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';

export default function Register() {
  const { user, loading, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '', first_name: '', last_name: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (loading) return null;
  if (user) return <Navigate to="/" replace />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register(form);
      navigate('/login');
    } catch (err) {
      const msgs = err.response?.data?.messages;
      if (msgs && typeof msgs === 'object') {
        setError(Object.values(msgs).flat().join('. '));
      } else {
        setError(err.response?.data?.message || 'Registration failed');
      }
    }
    setSubmitting(false);
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(ellipse at top, #111827 0%, #0A0E1A 70%)' }}>
      <Card sx={{ width: 440, maxWidth: '90vw' }}>
        <CardContent sx={{ p: 4 }}>
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <Box sx={{
              width: 56, height: 56, borderRadius: '50%', mx: 'auto', mb: 2,
              background: 'linear-gradient(135deg, #00D9FF, #34D399)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <PersonAddIcon sx={{ color: '#0A0E1A', fontSize: 28 }} />
            </Box>
            <Typography variant="h5" fontWeight={700}>Create Account</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              Get started with VoIP in minutes
            </Typography>
          </Box>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <form onSubmit={handleSubmit}>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <TextField fullWidth label="First Name" value={form.first_name} onChange={set('first_name')} margin="dense" />
              <TextField fullWidth label="Last Name" value={form.last_name} onChange={set('last_name')} margin="dense" />
            </Box>
            <TextField fullWidth label="Username" value={form.username} onChange={set('username')} margin="dense" required id="register-username" />
            <TextField fullWidth label="Email" type="email" value={form.email} onChange={set('email')} margin="dense" required id="register-email" />
            <TextField fullWidth label="Password" type="password" value={form.password} onChange={set('password')} margin="dense" required
              helperText="At least 8 characters with a digit and a letter" id="register-password" />
            <Button fullWidth type="submit" variant="contained" size="large"
              disabled={submitting} sx={{ mt: 2, py: 1.5 }} id="register-submit">
              {submitting ? <CircularProgress size={24} color="inherit" /> : 'Create Account'}
            </Button>
          </form>
          <Typography variant="body2" align="center" sx={{ mt: 2 }} color="text.secondary">
            Already have an account? <Link to="/login" style={{ color: '#00D9FF' }}>Sign In</Link>
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
}
