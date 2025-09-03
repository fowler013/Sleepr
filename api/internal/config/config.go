package config

import "os"

// Config holds all configuration for the application
type Config struct {
	DatabaseURL   string
	SleeperAPIURL string
	Port          string
	Environment   string
	JWTSecret     string
}

// Load loads configuration from environment variables
func Load() *Config {
	jwtSecret := getEnv("JWT_SECRET", "")
	if jwtSecret == "" {
		panic("JWT_SECRET environment variable is required for security")
	}

	return &Config{
		DatabaseURL:   getEnv("DATABASE_URL", "postgresql://localhost/sleepr?sslmode=disable"),
		SleeperAPIURL: getEnv("SLEEPER_API_BASE_URL", "https://api.sleeper.app/v1"),
		Port:          getEnv("PORT", "8080"),
		Environment:   getEnv("ENVIRONMENT", "development"),
		JWTSecret:     jwtSecret,
	}
}

// getEnv gets an environment variable with a fallback value
func getEnv(key, fallback string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return fallback
}
