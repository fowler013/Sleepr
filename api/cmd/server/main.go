// Package main provides the main entry point for the Sleepr API server
//
//	@title			Sleepr Fantasy Football API
//	@version		1.0
//	@description	A comprehensive Fantasy Football management API with advanced analytics
//	@termsOfService	http://swagger.io/terms/
//
//	@contact.name	Sleepr API Support
//	@contact.url	http://www.sleepr.io/support
//	@contact.email	support@sleepr.io
//
//	@license.name	MIT
//	@license.url	https://opensource.org/licenses/MIT
//
//	@host		localhost:8080
//	@BasePath	/api/v1
//
//	@securityDefinitions.apikey	BearerAuth
//	@in							header
//	@name						Authorization
//	@description				JWT token for API authentication. Format: Bearer {token}
package main

import (
	"log"

	_ "github.com/fowler013/sleepr/docs" // Import generated docs
	"github.com/fowler013/sleepr/internal/api"
	"github.com/fowler013/sleepr/internal/config"
	"github.com/fowler013/sleepr/internal/database"
	"github.com/joho/godotenv"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Printf("Warning: .env file not found: %v", err)
	}

	// Load configuration
	cfg := config.Load()

	// Connect to database
	db, err := database.Connect(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Initialize and start server
	server := api.NewServer(db, cfg)
	log.Printf("Starting server on port %s", cfg.Port)
	
	if err := server.Run(":" + cfg.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
