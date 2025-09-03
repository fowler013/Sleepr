-- Drop triggers
DROP TRIGGER IF EXISTS update_players_updated_at ON players;
DROP TRIGGER IF EXISTS update_teams_updated_at ON teams;
DROP TRIGGER IF EXISTS update_leagues_updated_at ON leagues;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

-- Drop trigger function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop indexes
DROP INDEX IF EXISTS idx_roster_players_player;
DROP INDEX IF EXISTS idx_roster_players_team;
DROP INDEX IF EXISTS idx_teams_user_id;
DROP INDEX IF EXISTS idx_teams_league_id;
DROP INDEX IF EXISTS idx_player_stats_player_week;
DROP INDEX IF EXISTS idx_players_is_active;
DROP INDEX IF EXISTS idx_players_team;
DROP INDEX IF EXISTS idx_players_position;

-- Drop tables (in reverse order due to foreign key constraints)
DROP TABLE IF EXISTS waiver_claims;
DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS roster_players;
DROP TABLE IF EXISTS player_stats;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS leagues;
DROP TABLE IF EXISTS users;
