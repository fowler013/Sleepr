package services

import (
	"database/sql"
	"fmt"

	"github.com/fowler013/sleepr/internal/models"
)

// UserService handles user-related operations
type UserService struct {
	db *sql.DB
}

// NewUserService creates a new UserService instance
func NewUserService(db *sql.DB) *UserService {
	return &UserService{db: db}
}

// Create creates a new user
func (s *UserService) Create(user *models.User) error {
	query := `
		INSERT INTO users (sleeper_id, username, display_name, email)
		VALUES ($1, $2, $3, $4)
		RETURNING id, created_at, updated_at
	`
	err := s.db.QueryRow(query, user.SleeperID, user.Username, user.DisplayName, user.Email).
		Scan(&user.ID, &user.CreatedAt, &user.UpdatedAt)
	
	return err
}

// GetByID retrieves a user by ID
func (s *UserService) GetByID(id int) (*models.User, error) {
	user := &models.User{}
	query := `
		SELECT id, sleeper_id, username, display_name, email, created_at, updated_at
		FROM users WHERE id = $1
	`
	
	err := s.db.QueryRow(query, id).Scan(
		&user.ID, &user.SleeperID, &user.Username,
		&user.DisplayName, &user.Email, &user.CreatedAt, &user.UpdatedAt,
	)
	
	if err != nil {
		return nil, err
	}
	
	return user, nil
}

// GetBySleeperID retrieves a user by Sleeper ID
func (s *UserService) GetBySleeperID(sleeperID string) (*models.User, error) {
	user := &models.User{}
	query := `
		SELECT id, sleeper_id, username, display_name, email, created_at, updated_at
		FROM users WHERE sleeper_id = $1
	`
	
	err := s.db.QueryRow(query, sleeperID).Scan(
		&user.ID, &user.SleeperID, &user.Username,
		&user.DisplayName, &user.Email, &user.CreatedAt, &user.UpdatedAt,
	)
	
	if err != nil {
		return nil, err
	}
	
	return user, nil
}

// TeamService handles team-related operations
type TeamService struct {
	db *sql.DB
}

// NewTeamService creates a new TeamService instance
func NewTeamService(db *sql.DB) *TeamService {
	return &TeamService{db: db}
}

// GetAll retrieves all teams
func (s *TeamService) GetAll() ([]models.Team, error) {
	var teams []models.Team
	query := `
		SELECT id, user_id, sleeper_id, league_id, name, owner, is_dynasty, 
		       settings, roster, created_at, updated_at
		FROM teams
		ORDER BY created_at DESC
	`
	
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	for rows.Next() {
		var team models.Team
		err := rows.Scan(
			&team.ID, &team.UserID, &team.SleeperID, &team.LeagueID,
			&team.Name, &team.Owner, &team.IsDynasty, &team.Settings,
			&team.Roster, &team.CreatedAt, &team.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		teams = append(teams, team)
	}
	
	return teams, nil
}

// GetByID retrieves a team by ID
func (s *TeamService) GetByID(id int) (*models.Team, error) {
	team := &models.Team{}
	query := `
		SELECT id, user_id, sleeper_id, league_id, name, owner, is_dynasty,
		       settings, roster, created_at, updated_at
		FROM teams WHERE id = $1
	`
	
	err := s.db.QueryRow(query, id).Scan(
		&team.ID, &team.UserID, &team.SleeperID, &team.LeagueID,
		&team.Name, &team.Owner, &team.IsDynasty, &team.Settings,
		&team.Roster, &team.CreatedAt, &team.UpdatedAt,
	)
	
	if err != nil {
		return nil, err
	}
	
	return team, nil
}

// SyncFromSleeper syncs team data from Sleeper API
func (s *TeamService) SyncFromSleeper(teamID string, sleeperService *SleeperService) error {
	// This is a placeholder - you'll implement the actual Sleeper API integration
	// For now, we'll just log that sync was requested
	fmt.Printf("Syncing team %s from Sleeper API\n", teamID)
	return nil
}

// PlayerService handles player-related operations
type PlayerService struct {
	db *sql.DB
}

// NewPlayerService creates a new PlayerService instance
func NewPlayerService(db *sql.DB) *PlayerService {
	return &PlayerService{db: db}
}

// GetAll retrieves all players
func (s *PlayerService) GetAll() ([]models.Player, error) {
	var players []models.Player
	query := `
		SELECT id, sleeper_id, name, position, team, age, years_exp,
		       fantasy_points, is_active, created_at, updated_at
		FROM players
		WHERE is_active = true
		ORDER BY fantasy_points DESC
	`
	
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	for rows.Next() {
		var player models.Player
		err := rows.Scan(
			&player.ID, &player.SleeperID, &player.Name, &player.Position,
			&player.Team, &player.Age, &player.YearsExp, &player.FantasyPoints,
			&player.IsActive, &player.CreatedAt, &player.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		players = append(players, player)
	}
	
	return players, nil
}

// GetByID retrieves a player by ID
func (s *PlayerService) GetByID(id int) (*models.Player, error) {
	player := &models.Player{}
	query := `
		SELECT id, sleeper_id, name, position, team, age, years_exp,
		       fantasy_points, is_active, created_at, updated_at
		FROM players WHERE id = $1
	`
	
	err := s.db.QueryRow(query, id).Scan(
		&player.ID, &player.SleeperID, &player.Name, &player.Position,
		&player.Team, &player.Age, &player.YearsExp, &player.FantasyPoints,
		&player.IsActive, &player.CreatedAt, &player.UpdatedAt,
	)
	
	if err != nil {
		return nil, err
	}
	
	return player, nil
}

// GetStats retrieves player statistics
func (s *PlayerService) GetStats(playerID int) ([]models.PlayerStats, error) {
	var stats []models.PlayerStats
	query := `
		SELECT id, player_id, week, season, fantasy_points, passing_yards,
		       passing_tds, rushing_yards, rushing_tds, receiving_yards,
		       receiving_tds, receptions
		FROM player_stats 
		WHERE player_id = $1
		ORDER BY season DESC, week DESC
	`
	
	rows, err := s.db.Query(query, playerID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	for rows.Next() {
		var stat models.PlayerStats
		err := rows.Scan(
			&stat.ID, &stat.PlayerID, &stat.Week, &stat.Season,
			&stat.FantasyPoints, &stat.PassingYards, &stat.PassingTDs,
			&stat.RushingYards, &stat.RushingTDs, &stat.ReceivingYards,
			&stat.ReceivingTDs, &stat.Receptions,
		)
		if err != nil {
			return nil, err
		}
		stats = append(stats, stat)
	}
	
	return stats, nil
}
