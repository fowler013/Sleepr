import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
} from '@mui/material';
import {
  Search,
  TrendingUp,
  TrendingDown,
  Add,
  Person,
  Sports,
} from '@mui/icons-material';

interface WaiverWirePlayer {
  player_id: number;
  name: string;
  position: string;
  team: string;
  recommendation_score: number;
  reason: string;
  projected_points?: number;
  availability?: number;
}

const WaiverWire: React.FC = () => {
  const [players, setPlayers] = useState<WaiverWirePlayer[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [positionFilter, setPositionFilter] = useState('ALL');

  // Mock data - replace with actual API calls
  const mockPlayers: WaiverWirePlayer[] = [
    {
      player_id: 1,
      name: "Tyler Huntley",
      position: "QB",
      team: "MIA",
      recommendation_score: 85,
      reason: "High upside backup with rushing ability",
      projected_points: 18.5,
      availability: 75,
    },
    {
      player_id: 2,
      name: "Kareem Hunt",
      position: "RB",
      team: "CLE",
      recommendation_score: 92,
      reason: "Proven veteran with goal-line opportunities",
      projected_points: 14.2,
      availability: 45,
    },
    {
      player_id: 3,
      name: "Darnell Mooney",
      position: "WR",
      team: "ATL",
      recommendation_score: 78,
      reason: "Deep threat with improved QB play",
      projected_points: 12.8,
      availability: 65,
    },
    {
      player_id: 4,
      name: "Cole Kmet",
      position: "TE",
      team: "CHI",
      recommendation_score: 71,
      reason: "Consistent target share in improved offense",
      projected_points: 9.5,
      availability: 80,
    },
    {
      player_id: 5,
      name: "Justice Hill",
      position: "RB",
      team: "BAL",
      recommendation_score: 68,
      reason: "Handcuff with standalone value",
      projected_points: 8.7,
      availability: 85,
    },
  ];

  useEffect(() => {
    loadWaiverWireRecommendations();
  }, []);

  const loadWaiverWireRecommendations = async () => {
    setLoading(true);
    try {
      // TODO: Replace with actual API call
      // const response = await api.getWaiverWireRecommendations();
      // setPlayers(response);
      
      // For now, use mock data
      setTimeout(() => {
        setPlayers(mockPlayers);
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to load waiver wire recommendations:', error);
      setPlayers(mockPlayers);
      setLoading(false);
    }
  };

  const filteredPlayers = players.filter(player => {
    const matchesSearch = player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         player.team.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPosition = positionFilter === 'ALL' || player.position === positionFilter;
    return matchesSearch && matchesPosition;
  });

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getAvailabilityColor = (availability: number) => {
    if (availability >= 70) return 'success';
    if (availability >= 50) return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Waiver Wire Recommendations
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          AI-powered player recommendations based on availability and upside
        </Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Search players or teams..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Position</InputLabel>
              <Select
                value={positionFilter}
                onChange={(e) => setPositionFilter(e.target.value)}
                label="Position"
              >
                <MenuItem value="ALL">All Positions</MenuItem>
                <MenuItem value="QB">QB</MenuItem>
                <MenuItem value="RB">RB</MenuItem>
                <MenuItem value="WR">WR</MenuItem>
                <MenuItem value="TE">TE</MenuItem>
                <MenuItem value="K">K</MenuItem>
                <MenuItem value="DEF">DEF</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="contained"
              onClick={loadWaiverWireRecommendations}
              disabled={loading}
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Top Picks</Typography>
              </Box>
              <Typography variant="h4">
                {filteredPlayers.filter(p => p.recommendation_score >= 80).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                High-value targets
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Person color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Available</Typography>
              </Box>
              <Typography variant="h4">
                {filteredPlayers.filter(p => (p.availability || 0) >= 70).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Widely available
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Sports color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Sleepers</Typography>
              </Box>
              <Typography variant="h4">
                {filteredPlayers.filter(p => p.recommendation_score >= 70 && (p.availability || 0) >= 80).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Hidden gems
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Add color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Total</Typography>
              </Box>
              <Typography variant="h4">
                {filteredPlayers.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Recommendations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Players Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Player</TableCell>
                <TableCell>Position</TableCell>
                <TableCell>Team</TableCell>
                <TableCell align="center">Score</TableCell>
                <TableCell align="center">Projected</TableCell>
                <TableCell align="center">Availability</TableCell>
                <TableCell>Recommendation Reason</TableCell>
                <TableCell align="center">Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredPlayers.map((player) => (
                <TableRow key={player.player_id} hover>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      {player.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={player.position} 
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{player.team}</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={player.recommendation_score}
                      color={getScoreColor(player.recommendation_score)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell align="center">
                    {player.projected_points?.toFixed(1)} pts
                  </TableCell>
                  <TableCell align="center">
                    <Chip
                      label={`${player.availability}%`}
                      color={getAvailabilityColor(player.availability || 0)}
                      size="small"
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {player.reason}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<Add />}
                      onClick={() => {
                        // TODO: Add to watchlist or claim
                        console.log(`Adding ${player.name} to watchlist`);
                      }}
                    >
                      Add
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {filteredPlayers.length === 0 && !loading && (
        <Alert severity="info" sx={{ mt: 2 }}>
          No players match your current filters. Try adjusting your search or position filter.
        </Alert>
      )}
    </Container>
  );
};

export default WaiverWire;
