import React from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  Button,
  Chip,
  Avatar,
  LinearProgress,
} from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  People, 
  EmojiEvents,
  Star,
  Refresh,
} from '@mui/icons-material';

interface Team {
  id: number;
  name: string;
  owner: string;
  is_dynasty: boolean;
  league_id: string;
  wins?: number;
  losses?: number;
  ties?: number;
  points_for?: number;
  points_against?: number;
  playoff_position?: number;
}

const Teams: React.FC = () => {
  // Mock data - replace with actual API calls
  const teams: Team[] = [
    {
      id: 1,
      name: "Dynasty Dominators",
      owner: "User",
      is_dynasty: true,
      league_id: "123456789",
      wins: 8,
      losses: 4,
      ties: 0,
      points_for: 1456.7,
      points_against: 1234.2,
      playoff_position: 2,
    },
    {
      id: 2,
      name: "Redraft Rockets",
      owner: "User",
      is_dynasty: false,
      league_id: "987654321",
      wins: 7,
      losses: 5,
      ties: 0,
      points_for: 1389.4,
      points_against: 1345.8,
      playoff_position: 4,
    },
    {
      id: 3,
      name: "Future Champions",
      owner: "User",
      is_dynasty: true,
      league_id: "456789123",
      wins: 6,
      losses: 6,
      ties: 0,
      points_for: 1234.9,
      points_against: 1289.1,
      playoff_position: 6,
    },
  ];

  const getWinPercentage = (wins: number, losses: number, ties: number) => {
    const total = wins + losses + ties;
    return total > 0 ? ((wins + ties * 0.5) / total * 100).toFixed(1) : '0.0';
  };

  const getPositionColor = (position: number) => {
    if (position <= 2) return 'success';
    if (position <= 4) return 'warning';
    return 'error';
  };

  const handleSyncTeam = (teamId: number) => {
    // TODO: Implement team sync with Sleeper API
    console.log(`Syncing team ${teamId}`);
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" gutterBottom>
          My Teams
        </Typography>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => {
            // TODO: Sync all teams
            console.log('Syncing all teams');
          }}
        >
          Sync All
        </Button>
      </Box>

      <Grid container spacing={3}>
        {teams.map((team) => (
          <Grid item xs={12} md={6} key={team.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {team.name}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                      <Chip 
                        label={team.is_dynasty ? "Dynasty" : "Redraft"} 
                        color={team.is_dynasty ? "primary" : "secondary"}
                        size="small"
                      />
                      <Chip 
                        label={`#${team.playoff_position}`}
                        color={getPositionColor(team.playoff_position || 12)}
                        size="small"
                        icon={<EmojiEvents />}
                      />
                    </Box>
                  </Box>
                  <Avatar sx={{ bgcolor: team.is_dynasty ? 'primary.main' : 'secondary.main' }}>
                    {team.is_dynasty ? <Star /> : <People />}
                  </Avatar>
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Record & Performance
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">
                      {team.wins}-{team.losses}-{team.ties} 
                      ({getWinPercentage(team.wins || 0, team.losses || 0, team.ties || 0)}%)
                    </Typography>
                    <Typography variant="body2">
                      PF: {team.points_for?.toFixed(1)} | PA: {team.points_against?.toFixed(1)}
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={parseFloat(getWinPercentage(team.wins || 0, team.losses || 0, team.ties || 0))}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button 
                    size="small" 
                    variant="outlined"
                    onClick={() => handleSyncTeam(team.id)}
                    startIcon={<Refresh />}
                  >
                    Sync
                  </Button>
                  <Button 
                    size="small" 
                    variant="contained"
                    startIcon={<TrendingUp />}
                  >
                    Analytics
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Dynasty Teams
            </Typography>
            <Typography variant="h3" color="primary">
              {teams.filter(t => t.is_dynasty).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Long-term investments
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Overall Win Rate
            </Typography>
            <Typography variant="h3" color="success.main">
              {(() => {
                const totalWins = teams.reduce((sum, t) => sum + (t.wins || 0), 0);
                const totalLosses = teams.reduce((sum, t) => sum + (t.losses || 0), 0);
                const totalTies = teams.reduce((sum, t) => sum + (t.ties || 0), 0);
                return getWinPercentage(totalWins, totalLosses, totalTies);
              })()}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Across all leagues
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Playoff Teams
            </Typography>
            <Typography variant="h3" color="warning.main">
              {teams.filter(t => (t.playoff_position || 12) <= 6).length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Currently in playoffs
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Teams;
