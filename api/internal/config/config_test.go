package config

import (
	"os"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConfigLoad(t *testing.T) {
	// Save original environment
	originalJWTSecret := os.Getenv("JWT_SECRET")
	defer func() {
		if originalJWTSecret != "" {
			os.Setenv("JWT_SECRET", originalJWTSecret)
		} else {
			os.Unsetenv("JWT_SECRET")
		}
	}()

	t.Run("ValidJWTSecret", func(t *testing.T) {
		os.Setenv("JWT_SECRET", "test-jwt-secret")
		
		config := Load()
		assert.NotNil(t, config)
		assert.Equal(t, "test-jwt-secret", config.JWTSecret)
	})

	t.Run("MissingJWTSecret", func(t *testing.T) {
		os.Unsetenv("JWT_SECRET")
		
		// This should panic
		assert.Panics(t, func() {
			Load()
		}, "Should panic when JWT_SECRET is missing")
	})

	t.Run("DefaultValues", func(t *testing.T) {
		os.Setenv("JWT_SECRET", "test-secret")
		
		config := Load()
		assert.Equal(t, "postgresql://localhost/sleepr?sslmode=disable", config.DatabaseURL)
		assert.Equal(t, "https://api.sleeper.app/v1", config.SleeperAPIURL)
		assert.Equal(t, "8080", config.Port)
		assert.Equal(t, "development", config.Environment)
	})

	t.Run("CustomEnvironmentValues", func(t *testing.T) {
		os.Setenv("JWT_SECRET", "test-secret")
		os.Setenv("DATABASE_URL", "custom-db-url")
		os.Setenv("PORT", "9090")
		os.Setenv("ENVIRONMENT", "production")
		
		defer func() {
			os.Unsetenv("DATABASE_URL")
			os.Unsetenv("PORT")
			os.Unsetenv("ENVIRONMENT")
		}()
		
		config := Load()
		assert.Equal(t, "custom-db-url", config.DatabaseURL)
		assert.Equal(t, "9090", config.Port)
		assert.Equal(t, "production", config.Environment)
	})
}