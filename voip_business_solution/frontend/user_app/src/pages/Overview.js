import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import {
  Box, Grid, Card, CardContent, Typography, Chip, Skeleton, LinearProgress,
} from '@mui/material';
import PhoneIcon from '@mui/icons-material/Phone';
import SmsIcon from '@mui/icons-material/Sms';
import TimerIcon from '@mui/icons-material/Timer';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';

export default function Overview() {
  const { user } = useAuth();
  const [sub, setSub] = useState(null);
  const [dids, setDids] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/subscriptions/current').then(r => setSub(r.data)).catch(() => {}),
      api.get('/dids/my-numbers').then(r => setDids(Array.isArray(r.data) ? r.data : [])).catch(() => {}),
    ]).finally(() => setLoading(false));
  }, []);

  const kycColor = { verified: 'success', pending: 'warning', unverified: 'default', rejected: 'error' };
  const usage = sub?.usage;
  const minutesPct = usage ? Math.min(100, ((usage.used_minutes || 0) / (usage.included_minutes || 1)) * 100) : 0;
  const smsPct = usage ? Math.min(100, ((usage.used_messages || 0) / (usage.included_messages || 1)) * 100) : 0;

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1 }}>Welcome back, {user?.first_name || user?.username}!</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Here's a quick look at your account
      </Typography>

      <Grid container spacing={3}>
        {/* KYC Status */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                <VerifiedUserIcon sx={{ color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">KYC Status</Typography>
              </Box>
              <Chip label={user?.kyc_status || 'unverified'} color={kycColor[user?.kyc_status] || 'default'} />
            </CardContent>
          </Card>
        </Grid>

        {/* Active Plan */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                <TimerIcon sx={{ color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">Active Plan</Typography>
              </Box>
              {loading ? <Skeleton width={80} /> : (
                <Typography variant="h6" fontWeight={700}>{sub?.plan_name || 'No Plan'}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Phone Numbers */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                <PhoneIcon sx={{ color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">My Numbers</Typography>
              </Box>
              {loading ? <Skeleton width={80} /> : (
                <Typography variant="h6" fontWeight={700}>{dids.length === 0 ? 'None' : dids.map(d => d.number).join(', ')}</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* SMS */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                <SmsIcon sx={{ color: 'primary.main' }} />
                <Typography variant="body2" color="text.secondary">Messages Left</Typography>
              </Box>
              {loading ? <Skeleton width={60} /> : (
                <Typography variant="h6" fontWeight={700}>
                  {usage ? `${(usage.included_messages || 0) - (usage.used_messages || 0)}` : '—'}
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Usage Bars */}
      {usage && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Usage This Billing Period</Typography>
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">Voice Minutes</Typography>
                <Typography variant="body2" color="text.secondary">{usage.used_minutes || 0} / {usage.included_minutes || 0}</Typography>
              </Box>
              <LinearProgress variant="determinate" value={minutesPct} sx={{
                height: 8, borderRadius: 4,
                bgcolor: 'rgba(0,217,255,0.1)',
                '& .MuiLinearProgress-bar': { borderRadius: 4, background: 'linear-gradient(90deg, #00D9FF, #34D399)' },
              }} />
            </Box>
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                <Typography variant="body2">SMS Messages</Typography>
                <Typography variant="body2" color="text.secondary">{usage.used_messages || 0} / {usage.included_messages || 0}</Typography>
              </Box>
              <LinearProgress variant="determinate" value={smsPct} sx={{
                height: 8, borderRadius: 4,
                bgcolor: 'rgba(255,101,132,0.1)',
                '& .MuiLinearProgress-bar': { borderRadius: 4, background: 'linear-gradient(90deg, #FF6584, #FBBF24)' },
              }} />
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
