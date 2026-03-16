import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import {
  Box, Typography, Card, CardContent, Grid, Button, Chip, Snackbar, Alert, Skeleton,
  Dialog, DialogTitle, DialogContent, DialogActions,
} from '@mui/material';

export default function Subscription() {
  const [plans, setPlans] = useState([]);
  const [current, setCurrent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [confirm, setConfirm] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get('/subscriptions/plans').then(r => setPlans(Array.isArray(r.data) ? r.data : r.data.plans || [])),
      api.get('/subscriptions/current').then(r => setCurrent(r.data)).catch(() => {}),
    ]).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const subscribe = async (planId) => {
    try {
      await api.post('/subscriptions/subscribe', { plan_id: planId });
      setToast({ severity: 'success', msg: 'Subscribed successfully!' });
      // Reload
      const { data } = await api.get('/subscriptions/current');
      setCurrent(data);
    } catch (e) {
      setToast({ severity: 'error', msg: e.response?.data?.message || 'Subscription failed' });
    }
    setConfirm(null);
  };

  const cancel = async () => {
    try {
      await api.post('/subscriptions/cancel');
      setToast({ severity: 'success', msg: 'Subscription cancelled' });
      setCurrent(null);
    } catch (e) {
      setToast({ severity: 'error', msg: e.response?.data?.message || 'Cancellation failed' });
    }
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1 }}>Subscription</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Choose a plan that fits your communication needs
      </Typography>

      {current && (
        <Card sx={{ mb: 3, borderColor: 'rgba(52,211,153,0.3)' }}>
          <CardContent sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Box>
              <Typography variant="h6" fontWeight={700}>{current.plan_name || 'Current Plan'}</Typography>
              <Typography variant="body2" color="text.secondary">
                Status: <Chip label={current.status || 'active'} color="success" size="small" sx={{ ml: 0.5 }} />
              </Typography>
            </Box>
            <Button variant="outlined" color="error" onClick={cancel}>Cancel Plan</Button>
          </CardContent>
        </Card>
      )}

      <Grid container spacing={3}>
        {loading ? [...Array(3)].map((_, i) => (
          <Grid item xs={12} sm={6} md={4} key={i}>
            <Card><CardContent><Skeleton height={180} /></CardContent></Card>
          </Grid>
        )) : plans.map((p) => {
          const isActive = current?.plan_id === p.id;
          return (
            <Grid item xs={12} sm={6} md={4} key={p.id || p.plan_code}>
              <Card sx={isActive ? { borderColor: 'rgba(52,211,153,0.4)', boxShadow: '0 0 20px rgba(52,211,153,0.08)' } : {}}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" fontWeight={700}>{p.plan_name}</Typography>
                      <Chip label={p.target_country} size="small" sx={{ mt: 0.5 }} />
                    </Box>
                    {isActive && <Chip label="Current" color="success" size="small" />}
                  </Box>
                  <Typography variant="h4" fontWeight={800} sx={{ my: 2 }}>
                    ${(p.monthly_fee || 0).toFixed(2)}
                    <Typography component="span" variant="body2" color="text.secondary">/mo</Typography>
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>{p.description || 'Standard VoIP plan'}</Typography>
                  <Box sx={{ my: 2 }}>
                    <Typography variant="body2">• {p.included_minutes} minutes included</Typography>
                    <Typography variant="body2">• {p.included_messages} SMS included</Typography>
                    <Typography variant="body2" color="text.secondary">• Voice overage: ${p.overage_rate_voice}/min</Typography>
                    <Typography variant="body2" color="text.secondary">• SMS overage: ${p.overage_rate_sms}/msg</Typography>
                  </Box>
                  <Button fullWidth variant={isActive ? 'outlined' : 'contained'} disabled={isActive}
                    onClick={() => setConfirm(p)} sx={{ mt: 1 }}>
                    {isActive ? 'Current Plan' : 'Subscribe'}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      <Dialog open={!!confirm} onClose={() => setConfirm(null)}>
        <DialogTitle>Subscribe to {confirm?.plan_name}?</DialogTitle>
        <DialogContent>
          <Typography>You'll be charged <b>${confirm?.monthly_fee?.toFixed(2)}/month</b>.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirm(null)}>Cancel</Button>
          <Button variant="contained" onClick={() => subscribe(confirm.id)}>Confirm</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        {toast && <Alert severity={toast.severity} onClose={() => setToast(null)}>{toast.msg}</Alert>}
      </Snackbar>
    </Box>
  );
}
