import React, { useEffect, useState, useCallback } from 'react';
import api from '../api/axios';
import {
  Box, Typography, Card, CardContent, Table, TableHead, TableBody, TableRow,
  TableCell, Chip, IconButton, TextField, InputAdornment, Skeleton, Snackbar, Alert,
  Dialog, DialogTitle, DialogContent, DialogActions, Button, TablePagination,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import BlockIcon from '@mui/icons-material/Block';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

const STATUS_COLOR = { true: 'success', false: 'error' };
const KYC_COLOR = { verified: 'success', pending: 'warning', unverified: 'default', rejected: 'error' };

export default function UsersManager() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [toast, setToast] = useState(null);
  const [confirm, setConfirm] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage] = useState(10);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = search ? { search } : {};
      const { data } = await api.get('/admin/users', { params });
      setUsers(Array.isArray(data) ? data : data.users || []);
    } catch { setToast({ severity: 'error', msg: 'Failed to load users' }); }
    setLoading(false);
  }, [search]);

  useEffect(() => { load(); }, [load]);

  const toggleStatus = async (userId, currentActive) => {
    const action = currentActive ? 'deactivate' : 'activate';
    try {
      await api.put(`/admin/users/${userId}/${action}`);
      setToast({ severity: 'success', msg: `User ${action}d` });
      load();
    } catch { setToast({ severity: 'error', msg: `Failed to ${action} user` }); }
    setConfirm(null);
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3 }}>User Management</Typography>
      <TextField fullWidth placeholder="Search by username or email…" value={search}
        onChange={(e) => setSearch(e.target.value)} sx={{ mb: 3 }} id="users-search"
        InputProps={{ startAdornment: <InputAdornment position="start"><SearchIcon color="action" /></InputAdornment> }} />
      <Card>
        <CardContent sx={{ p: 0, '&:last-child': { paddingBottom: 0 } }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell><TableCell>Username</TableCell><TableCell>Email</TableCell>
                <TableCell>Name</TableCell><TableCell>KYC</TableCell><TableCell>Status</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? [...Array(5)].map((_, i) => (
                <TableRow key={i}>{[...Array(7)].map((_, j) => <TableCell key={j}><Skeleton /></TableCell>)}</TableRow>
              )) : users.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((u) => (
                <TableRow key={u.id} hover>
                  <TableCell>{u.id}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{u.username}</TableCell>
                  <TableCell>{u.email}</TableCell>
                  <TableCell>{u.full_name || '—'}</TableCell>
                  <TableCell><Chip label={u.kyc_status || 'unverified'} color={KYC_COLOR[u.kyc_status] || 'default'} size="small" /></TableCell>
                  <TableCell><Chip label={u.is_active ? 'Active' : 'Inactive'} color={STATUS_COLOR[u.is_active]} size="small" variant="outlined" /></TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => setConfirm(u)}
                      sx={{ color: u.is_active ? 'error.main' : 'success.main' }}>
                      {u.is_active ? <BlockIcon fontSize="small" /> : <CheckCircleIcon fontSize="small" />}
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {!loading && <TablePagination component="div" count={users.length} page={page}
            onPageChange={(_, p) => setPage(p)} rowsPerPage={rowsPerPage} rowsPerPageOptions={[10]} />}
        </CardContent>
      </Card>

      <Dialog open={!!confirm} onClose={() => setConfirm(null)}>
        <DialogTitle>{confirm?.is_active ? 'Deactivate' : 'Activate'} User?</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to {confirm?.is_active ? 'deactivate' : 'activate'} <b>{confirm?.username}</b>?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirm(null)}>Cancel</Button>
          <Button variant="contained" color={confirm?.is_active ? 'error' : 'success'}
            onClick={() => toggleStatus(confirm.id, confirm.is_active)}>Confirm</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        {toast && <Alert severity={toast.severity} onClose={() => setToast(null)}>{toast.msg}</Alert>}
      </Snackbar>
    </Box>
  );
}
