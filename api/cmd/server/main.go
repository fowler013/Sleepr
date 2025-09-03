package main

import (
	"log"
	"os"

	"github.com/fowler013/sleepr/internal/api"
	"github.com/fowler013/sleepr/internal/config"
	"github.com/fowler013/sleepr/internal/database"
	"github.com/joho/godotenv"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	// Load configuration
	cfg := config.Load()

	// Initialize database
	db, err := database.NewConnection(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Run migrations
	if err := database.RunMigrations(cfg.DatabaseURL); err != nil {
		log.Fatalf("Failed to run migrations: %v", err)
	}

	// Initialize API server
	server := api.NewServer(db, cfg)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Starting server on port %s", port)
	if err := server.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
