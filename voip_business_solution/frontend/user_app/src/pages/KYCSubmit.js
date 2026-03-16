import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import {
  Box, Typography, Card, CardContent, Button, TextField, MenuItem, Snackbar, Alert,
  Chip, Stepper, Step, StepLabel,
} from '@mui/material';

const DOC_TYPES = ['passport', 'national_id', 'drivers_license'];

export default function KYCSubmit() {
  const { user, refreshUser } = useAuth();
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);
  const [form, setForm] = useState({
    document_type: 'passport', document_number: '', document_country: '',
    document_front_url: '', document_back_url: '', selfie_url: '',
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get('/kyc/records').then(r => setRecords(Array.isArray(r.data) ? r.data : []))
      .catch(() => {}).finally(() => setLoading(false));
  }, []);

  const hasPending = records.some(r => r.verification_status === 'pending');
  const kycStatus = user?.kyc_status || 'unverified';
  const kycColor = { verified: 'success', pending: 'warning', unverified: 'default', rejected: 'error' };
  const activeStep = kycStatus === 'verified' ? 3 : kycStatus === 'pending' ? 1 : 0;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/kyc/submit', form);
      setToast({ severity: 'success', msg: 'KYC submitted successfully!' });
      // Reload
      const { data } = await api.get('/kyc/records');
      setRecords(Array.isArray(data) ? data : []);
      refreshUser();
    } catch (e) {
      setToast({ severity: 'error', msg: e.response?.data?.message || 'Submission failed' });
    }
    setSubmitting(false);
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 1 }}>KYC Verification</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Verify your identity to unlock full account features
      </Typography>

      {/* Status Card */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Typography variant="h6">Verification Status:</Typography>
            <Chip label={kycStatus} color={kycColor[kycStatus]} />
          </Box>
          <Stepper activeStep={activeStep} alternativeLabel>
            <Step><StepLabel>Submit Documents</StepLabel></Step>
            <Step><StepLabel>Under Review</StepLabel></Step>
            <Step><StepLabel>Verified</StepLabel></Step>
          </Stepper>
        </CardContent>
      </Card>

      {/* Submission Form */}
      {kycStatus !== 'verified' && !hasPending && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Submit Identity Documents</Typography>
            <form onSubmit={handleSubmit}>
              <TextField select fullWidth label="Document Type" value={form.document_type}
                onChange={(e) => setForm({ ...form, document_type: e.target.value })} margin="dense">
                {DOC_TYPES.map(t => <MenuItem key={t} value={t}>{t.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</MenuItem>)}
              </TextField>
              <TextField fullWidth label="Document Number" value={form.document_number} required
                onChange={(e) => setForm({ ...form, document_number: e.target.value })} margin="dense" />
              <TextField fullWidth label="Issuing Country (e.g. USA, GBR)" value={form.document_country} required
                onChange={(e) => setForm({ ...form, document_country: e.target.value })} margin="dense" />
              <TextField fullWidth label="Front Document URL" value={form.document_front_url}
                onChange={(e) => setForm({ ...form, document_front_url: e.target.value })} margin="dense"
                helperText="Upload your document to a secure service and paste the URL" />
              <TextField fullWidth label="Back Document URL (optional)" value={form.document_back_url}
                onChange={(e) => setForm({ ...form, document_back_url: e.target.value })} margin="dense" />
              <TextField fullWidth label="Selfie URL (optional)" value={form.selfie_url}
                onChange={(e) => setForm({ ...form, selfie_url: e.target.value })} margin="dense" />
              <Button type="submit" variant="contained" size="large" disabled={submitting}
                sx={{ mt: 2, py: 1.5 }} fullWidth>
                {submitting ? 'Submitting…' : 'Submit for Verification'}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {hasPending && kycStatus !== 'verified' && (
        <Card>
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6">Your KYC submission is under review</Typography>
            <Typography color="text.secondary" sx={{ mt: 1 }}>
              This usually takes 1-2 business days. We'll notify you once it's processed.
            </Typography>
          </CardContent>
        </Card>
      )}

      <Snackbar open={!!toast} autoHideDuration={3000} onClose={() => setToast(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}>
        {toast && <Alert severity={toast.severity} onClose={() => setToast(null)}>{toast.msg}</Alert>}
      </Snackbar>
    </Box>
  );
}
