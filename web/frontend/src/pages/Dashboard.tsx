import React from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  People,
  Star,
  Assessment,
  Sync,
  Timeline,
} from '@mui/icons-material';
import { useAuth } from '../services/AuthContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  const statsCards = [
    {
      title: 'Dynasty Teams',
      value: '3',
      change: '+1 this season',
      icon: <People />,
      color: 'primary',
    },
    {
      title: 'Total Teams',
      value: '5',
      change: 'Across all leagues',
      icon: <Star />,
      color: 'secondary',
    },
    {
      title: 'Win Rate',
      value: '67%',
      change: '+5% this season',
      icon: <TrendingUp />,
      color: 'success',
    },
    {
      title: 'Rankings',
      value: '#2',
      change: 'Dynasty power rank',
      icon: <Assessment />,
      color: 'warning',
    },
  ];

  const recentActivity = [
    'Synchronized team data from Sleeper',
    'Generated waiver wire recommendations',
    'Updated player projections',
    'Analyzed trade opportunities',
  ];

  const upcomingTasks = [
    'Review trade proposals',
    'Set lineups for Week 12',
    'Check waiver wire',
    'Update player watchlist',
  ];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Welcome back, {user?.display_name || user?.username}!
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Here's your fantasy football overview
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {statsCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: 40,
                      height: 40,
                      borderRadius: 1,
                      bgcolor: `${card.color}.light`,
                      color: `${card.color}.main`,
                      mr: 2,
                    }}
                  >
                    {card.icon}
                  </Box>
                  <Typography variant="h6" component="div">
                    {card.title}
                  </Typography>
                </Box>
                <Typography variant="h4" gutterBottom>
                  {card.value}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {card.change}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Sync />}
                  sx={{ mb: 1 }}
                >
                  Sync Teams
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Assessment />}
                  sx={{ mb: 1 }}
                >
                  Analytics
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<TrendingUp />}
                >
                  Waiver Wire
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<Timeline />}
                >
                  Projections
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List dense>
              {recentActivity.map((activity, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Chip size="small" label={index + 1} />
                  </ListItemIcon>
                  <ListItemText primary={activity} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Upcoming Tasks */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Upcoming Tasks
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Grid container spacing={2}>
              {upcomingTasks.map((task, index) => (
                <Grid item xs={12} sm={6} md={3} key={index}>
                  <Card variant="outlined">
                    <CardContent sx={{ textAlign: 'center' }}>
                      <Typography variant="body2">{task}</Typography>
                      <Button size="small" sx={{ mt: 1 }}>
                        Complete
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;
