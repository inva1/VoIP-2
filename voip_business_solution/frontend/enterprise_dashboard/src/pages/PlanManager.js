import React, { useEffect, useState, useCallback } from 'react';
import api from '../api/axios';
import {
  Box, Typography, Card, CardContent, Table, TableHead, TableBody, TableRow,
  TableCell, Chip, Button, Snackbar, Alert, Skeleton, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Grid,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';

export default function PlanManager() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [dialog, setDialog] = useState(null); // null | 'create' | plan object for edit
  const [form, setForm] = useState({});

  const BLANK = {
    plan_code: '', plan_name: '', description: '', target_country: 'USA',
    monthly_fee: '', included_minutes: '', included_messages: '',
    overage_rate_voice: '', overage_rate_sms: '',
  };

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/subscriptions/plans');
      setPlans(Array.isArray(data) ? data : data.plans || []);
    } catch { setToast({ severity: 'error', msg: 'Failed to load plans' }); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const openCreate = () => { setForm({ ...BLANK }); setDialog('create'); };
  const openEdit = (plan) => { setForm({ ...plan }); setDialog(plan); };

  const handleSave = async () => {
    const payload = {
      ...form,
      monthly_fee: parseFloat(form.monthly_fee) || 0,
      included_minutes: parseInt(form.included_minutes) || 0,
      included_messages: parseInt(form.included_messages) || 0,
      overage_rate_voice: parseFloat(form.overage_rate_voice) || 0,
      overage_rate_sms: parseFloat(form.overage_rate_sms) || 0,
    };
    try {
      if (dialog === 'create') {
        await api.post('/admin/plans', payload);
        setToast({ severity: 'success', msg: 'Plan created' });
      } else {
        await api.put(`/admin/plans/${dialog.id}`, payload);
        setToast({ severity: 'success', msg: 'Plan updated' });
      }
      setDialog(null);
      load();
    } catch (e) {
      setToast({ severity: 'error', msg: e.response?.data?.message || 'Failed to save plan' });
    }
  };

  const field = (label, key, type = 'text') => (
    <TextField fullWidth label={label} value={form[key] ?? ''} type={type}
      onChange={(e) => setForm({ ...form, [key]: e.target.value })} margin="dense" size="small" />
  );

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Subscription Plans</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={openCreate} id="create-plan-btn">New Plan</Button>
      </Box>
      <Card>
        <CardContent sx={{ p: 0, '&:last-child': { paddingBottom: 0 } }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell><TableCell>Name</TableCell><TableCell>Country</TableCell>
                <TableCell align="right">Monthly Fee</TableCell><TableCell align="right">Minutes</TableCell>
                <TableCell align="right">Messages</TableCell><TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? [...Array(3)].map((_, i) => (
                <TableRow key={i}>{[...Array(8)].map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}</TableRow>
              )) : plans.length === 0 ? (
                <TableRow><TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">No plans yet. Create one to get started.</Typography>
                </TableCell></TableRow>
              ) : plans.map((p) => (
                <TableRow key={p.id || p.plan_code} hover>
                  <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>{p.plan_code}</TableCell>
                  <TableCell>{p.plan_name}</TableCell>
                  <TableCell><Chip label={p.target_country} size="small" /></TableCell>
                  <TableCell align="right">${(p.monthly_fee || 0).toFixed(2)}</TableCell>
                  <TableCell align="right">{p.included_minutes}</TableCell>
                  <TableCell align="right">{p.included_messages}</TableCell>
                  <TableCell><Chip label={p.is_active !== false ? 'Active' : 'Inactive'} color={p.is_active !== false ? 'success' : 'default'} size="small" variant="outlined" /></TableCell>
                  <TableCell align="right">
                    <Button size="small" startIcon={<EditIcon />} onClick={() => openEdit(p)}>Edit</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={!!dialog} onClose={() => setDialog(null)} maxWidth="sm" fullWidth>
        <DialogTitle>{dialog === 'create' ? 'Create Plan' : 'Edit Plan'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={1}>
            <Grid item xs={6}>{field('Plan Code', 'plan_code')}</Grid>
            <Grid item xs={6}>{field('Plan Name', 'plan_name')}</Grid>
            <Grid item xs={12}>{field('Description', 'description')}</Grid>
            <Grid item xs={6}>{field('Target Country', 'target_country')}</Grid>
            <Grid item xs={6}>{field('Monthly Fee ($)', 'monthly_fee', 'number')}</Grid>
            <Grid item xs={6}>{field('Included Minutes', 'included_minutes', 'number')}</Grid>
            <Grid item xs={6}>{field('Included Messages', 'included_messages', 'number')}</Grid>
            <Grid item xs={6}>{field('Voice Overage ($/min)', 'overage_rate_voice', 'number')}</Grid>
            <Grid item xs={6}>{field('SMS Overage ($/msg)', 'overage_rate_sms', 'number')}</Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(null)}>Cancel</Button>
          <Button variant="contained" onClick={handleSave}>{dialog === 'create' ? 'Create' : 'Save'}</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        {toast && <Alert severity={toast.severity} onClose={() => setToast(null)}>{toast.msg}</Alert>}
      </Snackbar>
    </Box>
  );
}
