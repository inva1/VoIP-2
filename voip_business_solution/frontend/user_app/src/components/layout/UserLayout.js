import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Box, Drawer, AppBar, Toolbar, Typography, List, ListItemButton,
  ListItemIcon, ListItemText, Avatar, IconButton, Divider,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import CardMembershipIcon from '@mui/icons-material/CardMembership';
import PhoneIcon from '@mui/icons-material/Phone';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import LogoutIcon from '@mui/icons-material/Logout';
import MenuIcon from '@mui/icons-material/Menu';

const DRAWER_WIDTH = 240;

const NAV = [
  { label: 'Overview', icon: <HomeIcon />, path: '/' },
  { label: 'Subscription', icon: <CardMembershipIcon />, path: '/subscription' },
  { label: 'My Numbers', icon: <PhoneIcon />, path: '/numbers' },
  { label: 'KYC Verification', icon: <VerifiedUserIcon />, path: '/kyc' },
];

export default function UserLayout() {
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
          background: 'linear-gradient(135deg, #00D9FF, #34D399)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          fontWeight: 800, letterSpacing: '-0.02em',
        }}>
          VoIP
        </Typography>
        <Typography variant="caption" color="text.secondary">Your Phone, Anywhere</Typography>
      </Box>
      <Divider sx={{ borderColor: 'rgba(0,217,255,0.12)' }} />
      <List sx={{ flex: 1, px: 1.5, py: 1 }}>
        {NAV.map(({ label, icon, path }) => {
          const active = location.pathname === path;
          return (
            <ListItemButton key={path} onClick={() => { navigate(path); setMobileOpen(false); }}
              sx={{
                borderRadius: 2, mb: 0.5,
                bgcolor: active ? 'rgba(0,217,255,0.1)' : 'transparent',
                '&:hover': { bgcolor: 'rgba(0,217,255,0.06)' },
              }}>
              <ListItemIcon sx={{ color: active ? 'primary.main' : 'text.secondary', minWidth: 40 }}>{icon}</ListItemIcon>
              <ListItemText primary={label} primaryTypographyProps={{ fontWeight: active ? 600 : 400, fontSize: '0.9rem' }} />
            </ListItemButton>
          );
        })}
      </List>
      <Divider sx={{ borderColor: 'rgba(0,217,255,0.12)' }} />
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar sx={{ width: 36, height: 36, bgcolor: 'primary.main', color: '#0A0E1A', fontSize: '0.85rem', fontWeight: 700 }}>
          {user.first_name?.[0] || user.username?.[0] || 'U'}
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
        borderBottom: '1px solid rgba(0,217,255,0.1)', boxShadow: 'none',
      }}>
        <Toolbar>
          <IconButton edge="start" onClick={() => setMobileOpen(!mobileOpen)}><MenuIcon /></IconButton>
          <Typography variant="h6" sx={{ ml: 1 }}>VoIP</Typography>
        </Toolbar>
      </AppBar>
      <Drawer variant="temporary" open={mobileOpen} onClose={() => setMobileOpen(false)}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH, bgcolor: 'background.paper' } }}>
        {drawer}
      </Drawer>
      <Drawer variant="permanent"
        sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH, bgcolor: 'background.paper', borderRight: '1px solid rgba(0,217,255,0.1)',
        }}}>
        {drawer}
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, width: { md: `calc(100% - ${DRAWER_WIDTH}px)` }, mt: { xs: 8, md: 0 } }}>
        <Outlet />
      </Box>
    </Box>
  );
}
