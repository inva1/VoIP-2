import React, { useEffect, useState, useCallback } from 'react';
import api from '../api/axios';
import {
  Box, Typography, Card, CardContent, Table, TableHead, TableBody, TableRow,
  TableCell, Button, Chip, Snackbar, Alert, Skeleton,
  Dialog, DialogTitle, DialogContent, DialogActions,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

export default function DIDManager() {
  const [myDids, setMyDids] = useState([]);
  const [available, setAvailable] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [confirm, setConfirm] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [mine, avail] = await Promise.all([
        api.get('/dids/my-numbers').then(r => Array.isArray(r.data) ? r.data : []),
        api.get('/dids/available').then(r => Array.isArray(r.data) ? r.data : []),
      ]);
      setMyDids(mine);
      setAvailable(avail);
    } catch { setToast({ severity: 'error', msg: 'Failed to load numbers' }); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const assign = async (didId) => {
    try {
      await api.post(`/dids/assign/${didId}`);
      setToast({ severity: 'success', msg: 'Number assigned!' });
      load();
    } catch (e) {
      setToast({ severity: 'error', msg: e.response?.data?.message || 'Failed to assign' });
    }
    setConfirm(null);
  };

  const release = async (didId) => {
    try {
      await api.post(`/dids/release/${didId}`);
      setToast({ severity: 'success', msg: 'Number released' });
      load();
    } catch (e) {
      setToast({ severity: 'error', msg: e.response?.data?.message || 'Failed to release' });
    }
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1 }}>My Phone Numbers</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Manage your assigned DIDs (Direct Inward Dialing numbers)
      </Typography>

      {/* My Numbers */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Assigned Numbers</Typography>
          {loading ? <Skeleton height={60} /> : myDids.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2 }}>You don't have any numbers yet. Browse available numbers below.</Typography>
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow><TableCell>Number</TableCell><TableCell>Country</TableCell><TableCell>Type</TableCell><TableCell align="right">Actions</TableCell></TableRow>
              </TableHead>
              <TableBody>
                {myDids.map((d) => (
                  <TableRow key={d.id} hover>
                    <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600, fontSize: '1rem' }}>{d.number}</TableCell>
                    <TableCell><Chip label={d.country_code} size="small" /></TableCell>
                    <TableCell>{d.number_type || 'local'}</TableCell>
                    <TableCell align="right">
                      <Button size="small" color="error" variant="outlined" onClick={() => release(d.id)}>Release</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Available Numbers */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Available Numbers</Typography>
          {loading ? <Skeleton height={100} /> : available.length === 0 ? (
            <Typography color="text.secondary" sx={{ py: 2 }}>No numbers available right now. Check back later.</Typography>
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow><TableCell>Number</TableCell><TableCell>Country</TableCell><TableCell>Area Code</TableCell>
                  <TableCell align="right">Monthly Cost</TableCell><TableCell align="right">Actions</TableCell></TableRow>
              </TableHead>
              <TableBody>
                {available.map((d) => (
                  <TableRow key={d.id} hover>
                    <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>{d.number}</TableCell>
                    <TableCell><Chip label={d.country_code} size="small" /></TableCell>
                    <TableCell>{d.area_code || '—'}</TableCell>
                    <TableCell align="right">${(d.monthly_cost || 0).toFixed(2)}</TableCell>
                    <TableCell align="right">
                      <Button size="small" variant="contained" startIcon={<AddIcon />}
                        onClick={() => setConfirm(d)}>Get Number</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Dialog open={!!confirm} onClose={() => setConfirm(null)}>
        <DialogTitle>Get Number {confirm?.number}?</DialogTitle>
        <DialogContent>
          <Typography>Monthly cost: <b>${confirm?.monthly_cost?.toFixed(2)}</b></Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirm(null)}>Cancel</Button>
          <Button variant="contained" onClick={() => assign(confirm.id)}>Confirm</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        {toast && <Alert severity={toast.severity} onClose={() => setToast(null)}>{toast.msg}</Alert>}
      </Snackbar>
    </Box>
  );
}
