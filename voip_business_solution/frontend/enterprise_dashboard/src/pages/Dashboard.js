import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import {
  Box, Grid, Card, CardContent, Typography, Skeleton, Chip,
} from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import PhoneIcon from '@mui/icons-material/Phone';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';

const STAT_CARDS = [
  { key: 'total_users', label: 'Total Users', icon: <PeopleIcon />, color: '#6C63FF' },
  { key: 'verified_users', label: 'KYC Verified', icon: <VerifiedUserIcon />, color: '#2DD4BF' },
  { key: 'active_subscriptions', label: 'Active Subs', icon: <AttachMoneyIcon />, color: '#FBBF24' },
  { key: 'total_dids', label: 'Assigned DIDs', icon: <PhoneIcon />, color: '#FF6584' },
];

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/admin/stats').then(({ data }) => setStats(data)).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const chartData = stats ? [
    { name: 'Users', value: stats.total_users || 0 },
    { name: 'Verified', value: stats.verified_users || 0 },
    { name: 'Subs', value: stats.active_subscriptions || 0 },
    { name: 'DIDs', value: stats.total_dids || stats.assigned_dids || 0 },
    { name: 'Calls', value: stats.total_calls || 0 },
    { name: 'SMS', value: stats.total_sms || 0 },
  ] : [];

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>Dashboard</Typography>
      <Grid container spacing={3}>
        {STAT_CARDS.map(({ key, label, icon, color }) => (
          <Grid item xs={12} sm={6} md={3} key={key}>
            <Card>
              <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{
                  width: 48, height: 48, borderRadius: 2,
                  bgcolor: `${color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  {React.cloneElement(icon, { sx: { color, fontSize: 26 } })}
                </Box>
                <Box>
                  {loading ? <Skeleton width={60} height={32} /> : (
                    <Typography variant="h5" fontWeight={700}>{stats?.[key] ?? 0}</Typography>
                  )}
                  <Typography variant="caption" color="text.secondary">{label}</Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>System Overview</Typography>
          {loading ? <Skeleton variant="rectangular" height={260} sx={{ borderRadius: 2 }} /> : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#9AA0A6" fontSize={12} />
                <YAxis stroke="#9AA0A6" fontSize={12} />
                <Tooltip contentStyle={{ background: '#1E2235', border: '1px solid rgba(108,99,255,0.2)', borderRadius: 8, color: '#E8EAED' }} />
                <Bar dataKey="value" fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6C63FF" />
                    <stop offset="100%" stopColor="#9D97FF" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {stats && (
        <Box sx={{ mt: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label={`${stats.pending_kyc ?? 0} Pending KYC`} color="warning" variant="outlined" />
          <Chip label={`${stats.total_calls ?? 0} Total Calls`} color="primary" variant="outlined" />
          <Chip label={`${stats.total_sms ?? 0} SMS Sent`} color="secondary" variant="outlined" />
        </Box>
      )}
    </Box>
  );
}
