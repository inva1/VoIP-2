import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Box, Drawer, AppBar, Toolbar, Typography, List, ListItemButton,
  ListItemIcon, ListItemText, Avatar, IconButton, Divider, Chip,
} from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PeopleIcon from '@mui/icons-material/People';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import CardMembershipIcon from '@mui/icons-material/CardMembership';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';

const DRAWER_WIDTH = 260;

const NAV = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { label: 'Users', icon: <PeopleIcon />, path: '/users' },
  { label: 'KYC Review', icon: <VerifiedUserIcon />, path: '/kyc' },
  { label: 'Plans', icon: <CardMembershipIcon />, path: '/plans' },
];

export default function AdminLayout() {
  const { user, loading, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;

  const handleLogout = async () => { await logout(); navigate('/login'); };

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Box sx={{ p: 2.5, textAlign: 'center' }}>
        <Typography variant="h6" sx={{
          background: 'linear-gradient(135deg, #6C63FF, #FF6584)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          fontWeight: 800, letterSpacing: '-0.02em',
        }}>
          VoIP Admin
        </Typography>
        <Chip label="Enterprise" size="small" color="primary" variant="outlined" sx={{ mt: 0.5, fontSize: '0.65rem' }} />
      </Box>
      <Divider sx={{ borderColor: 'rgba(108,99,255,0.15)' }} />
      <List sx={{ flex: 1, px: 1.5, py: 1 }}>
        {NAV.map(({ label, icon, path }) => {
          const active = location.pathname === path;
          return (
            <ListItemButton key={path} onClick={() => { navigate(path); setMobileOpen(false); }}
              sx={{
                borderRadius: 2, mb: 0.5,
                bgcolor: active ? 'rgba(108,99,255,0.12)' : 'transparent',
                '&:hover': { bgcolor: 'rgba(108,99,255,0.08)' },
              }}>
              <ListItemIcon sx={{ color: active ? 'primary.main' : 'text.secondary', minWidth: 40 }}>{icon}</ListItemIcon>
              <ListItemText primary={label} primaryTypographyProps={{ fontWeight: active ? 600 : 400, fontSize: '0.9rem' }} />
            </ListItemButton>
          );
        })}
      </List>
      <Divider sx={{ borderColor: 'rgba(108,99,255,0.15)' }} />
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main', fontSize: '0.85rem' }}>
          {user.first_name?.[0] || user.username?.[0] || 'A'}
        </Avatar>
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <Typography variant="body2" noWrap fontWeight={600}>{user.full_name || user.username}</Typography>
          <Typography variant="caption" color="text.secondary" noWrap>{user.email}</Typography>
        </Box>
        <IconButton size="small" onClick={handleLogout} sx={{ color: 'text.secondary' }}><LogoutIcon fontSize="small" /></IconButton>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppBar position="fixed" sx={{
        display: { md: 'none' }, bgcolor: 'background.paper',
        borderBottom: '1px solid rgba(108,99,255,0.12)', boxShadow: 'none',
      }}>
        <Toolbar>
          <IconButton edge="start" onClick={() => setMobileOpen(!mobileOpen)}><MenuIcon /></IconButton>
          <Typography variant="h6" sx={{ ml: 1 }}>VoIP Admin</Typography>
        </Toolbar>
      </AppBar>
      <Drawer variant="temporary" open={mobileOpen} onClose={() => setMobileOpen(false)}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH, bgcolor: 'background.paper' } }}>
        {drawer}
      </Drawer>
      <Drawer variant="permanent"
        sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH, bgcolor: 'background.paper', borderRight: '1px solid rgba(108,99,255,0.12)',
        }}}>
        {drawer}
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { md: `calc(100% - ${DRAWER_WIDTH}px)` }, mt: { xs: 8, md: 0 } }}>
        <Outlet />
      </Box>
    </Box>
  );
}
