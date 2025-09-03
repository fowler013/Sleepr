package api

import (
	"database/sql"
	"fmt"
	"testing"

	"github.com/fowler013/sleepr/internal/models"
	"github.com/fowler013/sleepr/internal/services"
	_ "github.com/lib/pq"
)

func TestUserService(t *testing.T) {
	// This would require a test database setup
	// For now, we'll skip the actual database test
	t.Skip("Database tests require test database setup")

	db, err := sql.Open("postgres", "postgresql://localhost/sleepr_test?sslmode=disable")
	if err != nil {
		t.Fatalf("Failed to connect to test database: %v", err)
	}
	defer db.Close()

	userService := services.NewUserService(db)

	// Test creating a user
	user := &models.User{
		SleeperID:   "test123",
		Username:    "testuser",
		DisplayName: "Test User",
		Email:       "test@example.com",
	}

	err = userService.Create(user)
	if err != nil {
		t.Errorf("Failed to create user: %v", err)
	}

	// Test retrieving the user
	retrievedUser, err := userService.GetByID(user.ID)
	if err != nil {
		t.Errorf("Failed to retrieve user: %v", err)
	}

	if retrievedUser.Username != user.Username {
		t.Errorf("Expected username %s, got %s", user.Username, retrievedUser.Username)
	}
}

func TestPlayerService(t *testing.T) {
	// Similar to UserService test - would require test database
	t.Skip("Database tests require test database setup")
}

func Example() {
	// Example of how to use the API
	fmt.Println("Sleepr Fantasy Football API")
	fmt.Println("GET /api/v1/teams - List all teams")
	fmt.Println("GET /api/v1/players - List all players")
	fmt.Println("POST /api/v1/teams/:id/sync - Sync team from Sleeper")
	// Output:
	// Sleepr Fantasy Football API
	// GET /api/v1/teams - List all teams
	// GET /api/v1/players - List all players
	// POST /api/v1/teams/:id/sync - Sync team from Sleeper
}
