package models

import "time"

// User represents a fantasy football user
type User struct {
	ID          int       `json:"id" db:"id"`
	SleeperID   string    `json:"sleeper_id" db:"sleeper_id"`
	Username    string    `json:"username" db:"username"`
	DisplayName string    `json:"display_name" db:"display_name"`
	Email       string    `json:"email" db:"email"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

// Team represents a fantasy football team
type Team struct {
	ID        int       `json:"id" db:"id"`
	UserID    int       `json:"user_id" db:"user_id"`
	SleeperID string    `json:"sleeper_id" db:"sleeper_id"`
	LeagueID  string    `json:"league_id" db:"league_id"`
	Name      string    `json:"name" db:"name"`
	Owner     string    `json:"owner" db:"owner"`
	IsDynasty bool      `json:"is_dynasty" db:"is_dynasty"`
	Settings  string    `json:"settings" db:"settings"` // JSON field
	Roster    string    `json:"roster" db:"roster"`     // JSON field
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// Player represents a fantasy football player
type Player struct {
	ID            int       `json:"id" db:"id"`
	SleeperID     string    `json:"sleeper_id" db:"sleeper_id"`
	Name          string    `json:"name" db:"name"`
	Position      string    `json:"position" db:"position"`
	Team          string    `json:"team" db:"team"`
	Age           int       `json:"age" db:"age"`
	YearsExp      int       `json:"years_exp" db:"years_exp"`
	FantasyPoints float64   `json:"fantasy_points" db:"fantasy_points"`
	IsActive      bool      `json:"is_active" db:"is_active"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
}

// PlayerStats represents player statistics
type PlayerStats struct {
	ID             int     `json:"id" db:"id"`
	PlayerID       int     `json:"player_id" db:"player_id"`
	Week           int     `json:"week" db:"week"`
	Season         int     `json:"season" db:"season"`
	FantasyPoints  float64 `json:"fantasy_points" db:"fantasy_points"`
	PassingYards   int     `json:"passing_yards" db:"passing_yards"`
	PassingTDs     int     `json:"passing_tds" db:"passing_tds"`
	RushingYards   int     `json:"rushing_yards" db:"rushing_yards"`
	RushingTDs     int     `json:"rushing_tds" db:"rushing_tds"`
	ReceivingYards int     `json:"receiving_yards" db:"receiving_yards"`
	ReceivingTDs   int     `json:"receiving_tds" db:"receiving_tds"`
	Receptions     int     `json:"receptions" db:"receptions"`
}

// TeamRecommendation represents improvement recommendations for a team
type TeamRecommendation struct {
	TeamID      int                    `json:"team_id"`
	Type        string                 `json:"type"`     // "trade", "waiver", "lineup"
	Priority    string                 `json:"priority"` // "high", "medium", "low"
	Description string                 `json:"description"`
	Players     []PlayerRecommendation `json:"players"`
	Confidence  float64                `json:"confidence"`
}

// PlayerRecommendation represents a player-specific recommendation
type PlayerRecommendation struct {
	PlayerID     int     `json:"player_id"`
	PlayerName   string  `json:"player_name"`
	Action       string  `json:"action"` // "add", "drop", "trade", "start", "bench"
	Reason       string  `json:"reason"`
	ProjectedPts float64 `json:"projected_pts"`
}

// PlayerProjection represents future performance projections
type PlayerProjection struct {
	PlayerID     int     `json:"player_id"`
	PlayerName   string  `json:"player_name"`
	Week         int     `json:"week"`
	ProjectedPts float64 `json:"projected_pts"`
	Confidence   float64 `json:"confidence"`
	Ceiling      float64 `json:"ceiling"`
	Floor        float64 `json:"floor"`
	Trending     string  `json:"trending"` // "up", "down", "stable"
}
