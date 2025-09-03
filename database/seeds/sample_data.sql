-- Sample data for Sleepr Fantasy Football App
-- This file provides initial data for development and testing

-- Insert sample users
INSERT INTO users (sleeper_id, username, display_name, email) VALUES 
('user1', 'fantasy_guru', 'Fantasy Guru', 'guru@example.com'),
('user2', 'dynasty_king', 'Dynasty King', 'king@example.com'),
('user3', 'waiver_wizard', 'Waiver Wizard', 'wizard@example.com')
ON CONFLICT (sleeper_id) DO NOTHING;

-- Insert sample leagues
INSERT INTO leagues (sleeper_id, name, season, status, is_dynasty, scoring_settings, roster_positions) VALUES 
('league1', 'Championship Dynasty League', 2024, 'active', true, 
 '{"passing_td": 4, "rushing_td": 6, "receiving_td": 6, "ppr": 1}',
 '["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "DST", "K"]'),
('league2', 'Redraft League', 2024, 'active', false,
 '{"passing_td": 4, "rushing_td": 6, "receiving_td": 6, "ppr": 0.5}',
 '["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "DST", "K"]')
ON CONFLICT (sleeper_id) DO NOTHING;

-- Insert sample teams
INSERT INTO teams (user_id, sleeper_id, league_id, name, owner, is_dynasty, settings, roster) VALUES 
(1, 'team1', 'league1', 'Dynasty Dominators', 'fantasy_guru', true, '{}', '[]'),
(2, 'team2', 'league1', 'Future Champions', 'dynasty_king', true, '{}', '[]'),
(1, 'team3', 'league2', 'Waiver Wire Warriors', 'fantasy_guru', false, '{}', '[]')
ON CONFLICT (sleeper_id, league_id) DO NOTHING;

-- Insert sample players
INSERT INTO players (sleeper_id, name, position, team, age, years_exp, fantasy_points, is_active) VALUES 
('player1', 'Josh Allen', 'QB', 'BUF', 28, 7, 285.4, true),
('player2', 'Christian McCaffrey', 'RB', 'SF', 28, 8, 245.8, true),
('player3', 'Cooper Kupp', 'WR', 'LAR', 31, 7, 198.5, true),
('player4', 'Travis Kelce', 'TE', 'KC', 35, 12, 185.2, true),
('player5', 'Derrick Henry', 'RB', 'BAL', 30, 9, 165.3, true),
('player6', 'Tyreek Hill', 'WR', 'MIA', 30, 8, 210.7, true),
('player7', 'Lamar Jackson', 'QB', 'BAL', 27, 7, 278.9, true),
('player8', 'Davante Adams', 'WR', 'LV', 32, 11, 189.4, true),
('player9', 'Mark Andrews', 'TE', 'BAL', 29, 7, 145.6, true),
('player10', 'Saquon Barkley', 'RB', 'PHI', 27, 7, 195.2, true)
ON CONFLICT (sleeper_id) DO NOTHING;

-- Insert sample player stats (current season)
INSERT INTO player_stats (player_id, week, season, fantasy_points, passing_yards, passing_tds, rushing_yards, rushing_tds, receiving_yards, receiving_tds, receptions) VALUES 
-- Josh Allen stats
(1, 1, 2024, 24.5, 275, 2, 45, 1, 0, 0, 0),
(1, 2, 2024, 18.7, 215, 1, 25, 0, 0, 0, 0),
(1, 3, 2024, 32.1, 320, 3, 55, 1, 0, 0, 0),

-- Christian McCaffrey stats  
(2, 1, 2024, 28.4, 0, 0, 125, 2, 45, 0, 4),
(2, 2, 2024, 15.8, 0, 0, 85, 1, 35, 0, 3),
(2, 3, 2024, 22.3, 0, 0, 110, 1, 65, 1, 5),

-- Cooper Kupp stats
(3, 1, 2024, 16.7, 0, 0, 0, 0, 95, 1, 8),
(3, 2, 2024, 12.4, 0, 0, 0, 0, 75, 0, 6),
(3, 3, 2024, 19.8, 0, 0, 0, 0, 120, 1, 9)
ON CONFLICT (player_id, week, season) DO NOTHING;

-- Insert sample roster relationships
INSERT INTO roster_players (team_id, player_id, position, is_starter) VALUES 
-- Dynasty Dominators roster
(1, 1, 'QB', true),
(1, 2, 'RB', true),
(1, 5, 'RB', false),
(1, 3, 'WR', true),
(1, 6, 'WR', true),
(1, 4, 'TE', true),

-- Future Champions roster  
(2, 7, 'QB', true),
(2, 10, 'RB', true),
(2, 8, 'WR', true),
(2, 9, 'TE', true)
ON CONFLICT (team_id, player_id) DO NOTHING;

-- Create some indexes for better performance on sample data
CREATE INDEX IF NOT EXISTS idx_sample_player_stats_season ON player_stats(season, week);
CREATE INDEX IF NOT EXISTS idx_sample_players_position_team ON players(position, team);

-- Update sequences to avoid conflicts
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('teams_id_seq', (SELECT MAX(id) FROM teams));
SELECT setval('players_id_seq', (SELECT MAX(id) FROM players));
SELECT setval('player_stats_id_seq', (SELECT MAX(id) FROM player_stats));
SELECT setval('roster_players_id_seq', (SELECT MAX(id) FROM roster_players));

-- Show summary of inserted data
SELECT 'Users' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'Leagues', COUNT(*) FROM leagues  
UNION ALL
SELECT 'Teams', COUNT(*) FROM teams
UNION ALL
SELECT 'Players', COUNT(*) FROM players
UNION ALL
SELECT 'Player Stats', COUNT(*) FROM player_stats
UNION ALL
SELECT 'Roster Players', COUNT(*) FROM roster_players;
