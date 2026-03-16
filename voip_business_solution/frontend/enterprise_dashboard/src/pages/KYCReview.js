import React, { useEffect, useState, useCallback } from 'react';
import api from '../api/axios';
import {
  Box, Typography, Card, CardContent, Table, TableHead, TableBody, TableRow,
  TableCell, Chip, Button, Snackbar, Alert, Skeleton, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

export default function KYCReview() {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [review, setReview] = useState(null);
  const [notes, setNotes] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/admin/kyc/pending');
      setRecords(Array.isArray(data) ? data : data.records || []);
    } catch {
      // Fallback: try fetching all KYC records via admin users
      try {
        const { data } = await api.get('/admin/users');
        const users = Array.isArray(data) ? data : data.users || [];
        const pendingUsers = users.filter(u => u.kyc_status === 'pending');
        // Build a simplified list
        setRecords(pendingUsers.map(u => ({
          id: u.id, user_id: u.id, username: u.username, email: u.email,
          document_type: 'unknown', verification_status: 'pending',
        })));
      } catch { setToast({ severity: 'error', msg: 'Failed to load KYC records' }); }
    }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleReview = async (status) => {
    if (!review) return;
    try {
      await api.put(`/api/kyc/review/${review.id}`, {
        verification_status: status,
        notes: notes || undefined,
      });
      setToast({ severity: 'success', msg: `KYC ${status}` });
      setReview(null);
      setNotes('');
      load();
    } catch {
      setToast({ severity: 'error', msg: `Failed to ${status} KYC` });
    }
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1 }}>KYC Review</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Review and approve/reject pending identity verifications
      </Typography>
      <Card>
        <CardContent sx={{ p: 0, '&:last-child': { paddingBottom: 0 } }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell><TableCell>User</TableCell>
                <TableCell>Document Type</TableCell><TableCell>Country</TableCell>
                <TableCell>Status</TableCell><TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? [...Array(3)].map((_, i) => (
                <TableRow key={i}>{[...Array(6)].map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}</TableRow>
              )) : records.length === 0 ? (
                <TableRow><TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">No pending KYC submissions</Typography>
                </TableCell></TableRow>
              ) : records.map((r) => (
                <TableRow key={r.id} hover>
                  <TableCell>{r.id}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{r.username || `User #${r.user_id}`}</TableCell>
                  <TableCell>{r.document_type}</TableCell>
                  <TableCell>{r.document_country || '—'}</TableCell>
                  <TableCell><Chip label={r.verification_status} color="warning" size="small" /></TableCell>
                  <TableCell align="right" sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                    <Button size="small" color="success" startIcon={<CheckCircleIcon />}
                      onClick={() => setReview(r)} variant="outlined">Approve</Button>
                    <Button size="small" color="error" startIcon={<CancelIcon />}
                      onClick={() => { setReview(r); setNotes(''); }} variant="outlined">Reject</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={!!review} onClose={() => setReview(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Review KYC #{review?.id}</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            User: <b>{review?.username || `#${review?.user_id}`}</b> — Document: <b>{review?.document_type}</b>
          </Typography>
          <TextField fullWidth multiline rows={3} label="Review Notes (optional)" value={notes}
            onChange={(e) => setNotes(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReview(null)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={() => handleReview('rejected')}>Reject</Button>
          <Button variant="contained" color="success" onClick={() => handleReview('approved')}>Approve</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        {toast && <Alert severity={toast.severity} onClose={() => setToast(null)}>{toast.msg}</Alert>}
      </Snackbar>
    </Box>
  );
}
