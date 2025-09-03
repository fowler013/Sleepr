import React, { useState, FormEvent } from 'react';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  Box,
  Divider,
} from '@mui/material';
import { useAuth } from '../services/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [sleeperId, setSleeperId] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!username.trim() || !sleeperId.trim()) {
      setError('Please enter both username and Sleeper ID');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await login(username.trim(), sleeperId.trim());
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ padding: 4, width: '100%' }}>
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Sleepr
          </Typography>
          <Typography variant="subtitle1" align="center" color="text.secondary" gutterBottom>
            Fantasy Football Dynasty Management
          </Typography>
          
          <Divider sx={{ my: 3 }} />

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
            
            <TextField
              margin="normal"
              required
              fullWidth
              id="sleeper_id"
              label="Sleeper User ID"
              name="sleeper_id"
              helperText="Your Sleeper User ID (numeric)"
              value={sleeperId}
              onChange={(e) => setSleeperId(e.target.value)}
              disabled={loading}
            />
            
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
            
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>How to find your Sleeper User ID:</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                1. Open the Sleeper app
              </Typography>
              <Typography variant="body2" color="text.secondary">
                2. Go to your profile
              </Typography>
              <Typography variant="body2" color="text.secondary">
                3. Your User ID is in the URL or displayed in settings
              </Typography>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Login;
