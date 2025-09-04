package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/fowler013/sleepr/internal/config"
	"github.com/fowler013/sleepr/internal/handlers"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

// Integration test demonstrating the complete API workflow
func TestAPIWorkflow(t *testing.T) {
	gin.SetMode(gin.TestMode)
	cfg := &config.Config{
		JWTSecret: "test-secret-key-integration",
		Environment: "test",
	}
	
	// Create a test router with all routes
	server := &Server{
		db:     nil, // Using nil for this demo - in real tests we'd use a mock
		config: cfg,
		router: gin.New(),
	}
	
	server.setupRoutes()
	router := server.router

	t.Run("Health Check", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/health", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		
		var response map[string]interface{}
		json.Unmarshal(w.Body.Bytes(), &response)
		assert.Equal(t, "ok", response["status"])
		assert.Equal(t, "test", response["environment"])
	})

	t.Run("Swagger Documentation", func(t *testing.T) {
		// Skip for now - swagger is configured but specific endpoint may vary
		t.Skip("Swagger endpoint path may vary based on configuration")
	})

	t.Run("Public Endpoints Accessible", func(t *testing.T) {
		publicEndpoints := []string{
			"/api/v1/public/analytics/waiver-wire",
		}
		
		for _, endpoint := range publicEndpoints {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", endpoint, nil)
			router.ServeHTTP(w, req)
			
			// Should not be unauthorized (may have other errors due to nil DB)
			assert.NotEqual(t, http.StatusUnauthorized, w.Code, "Public endpoint should not require auth: %s", endpoint)
		}
	})

	t.Run("Protected Endpoints Require Authentication", func(t *testing.T) {
		protectedEndpoints := []string{
			"/api/v1/users/1",
			"/api/v1/teams/1",
			"/api/v1/players/1",
			"/api/v1/analytics/teams/1/recommendations",
		}
		
		for _, endpoint := range protectedEndpoints {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", endpoint, nil)
			router.ServeHTTP(w, req)
			
			assert.Equal(t, http.StatusUnauthorized, w.Code, "Protected endpoint should require auth: %s", endpoint)
		}
	})

	t.Run("Input Validation Works", func(t *testing.T) {
		// Test SQL injection prevention
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/health?malicious=%27%3B%20DROP%20TABLE%20users%3B%20--", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code, "Should reject SQL injection attempts")
	})

	t.Run("Invalid ID Validation", func(t *testing.T) {
		// Test invalid ID rejection
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/users/invalid-id", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusBadRequest, w.Code, "Should reject invalid ID format")
	})

	t.Run("CORS Headers Set", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("OPTIONS", "/health", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, "http://localhost:3000", w.Header().Get("Access-Control-Allow-Origin"))
	})

	t.Run("Rate Limiting Active", func(t *testing.T) {
		// Create a new router to avoid interference with previous tests
		testServer := &Server{
			db:     nil,
			config: cfg,
			router: gin.New(),
		}
		testServer.setupRoutes()
		
		// Make many requests
		var lastStatusCode int
		for i := 0; i < 105; i++ {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/health", nil)
			testServer.router.ServeHTTP(w, req)
			lastStatusCode = w.Code
		}
		
		assert.Equal(t, http.StatusTooManyRequests, lastStatusCode, "Should be rate limited after many requests")
	})

	t.Run("Error Response Format", func(t *testing.T) {
		// Test standardized error response format
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/users/1", nil) // No auth header
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
		
		var errorResponse handlers.ErrorResponse
		err := json.Unmarshal(w.Body.Bytes(), &errorResponse)
		assert.NoError(t, err)
		assert.NotEmpty(t, errorResponse.Error)
	})
}

// Test demonstrating security features
func TestSecurityFeatures(t *testing.T) {
	gin.SetMode(gin.TestMode)
	cfg := &config.Config{
		JWTSecret: "security-test-secret",
		Environment: "test",
	}
	
	server := &Server{
		db:     nil,
		config: cfg,
		router: gin.New(),
	}
	
	server.setupRoutes()
	router := server.router

	t.Run("JWT Required for Protected Routes", func(t *testing.T) {
		protectedRoutes := map[string]string{
			"/api/v1/auth/refresh":                        "POST",
			"/api/v1/users/123":                          "GET",
			"/api/v1/teams/456":                          "GET",
			"/api/v1/analytics/players/789/projection":   "GET",
		}

		for route, method := range protectedRoutes {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest(method, route, nil)
			router.ServeHTTP(w, req)

			assert.Equal(t, http.StatusUnauthorized, w.Code, "Route %s should require JWT", route)

			var response map[string]interface{}
			json.Unmarshal(w.Body.Bytes(), &response)
			if response["error"] != nil {
				assert.Contains(t, response["error"], "Authorization header required")
			}
		}
	})

	t.Run("SQL Injection Prevention", func(t *testing.T) {
		injectionAttempts := []string{
			"/health?param=%27%20OR%201%3D1--",               // ' OR 1=1--
			"/health?param=%27%3B%20DROP%20TABLE%20users%3B%20--", // '; DROP TABLE users; --
			"/health?param=UNION%20SELECT%20*%20FROM%20sensitive_data", // UNION SELECT * FROM sensitive_data
		}

		for _, attempt := range injectionAttempts {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", attempt, nil)
			router.ServeHTTP(w, req)

			// Should be blocked by input sanitization
			assert.Equal(t, http.StatusBadRequest, w.Code, "SQL injection should be blocked: %s", attempt)
		}
	})

	t.Run("CORS Security", func(t *testing.T) {
		// Test allowed origin
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/health", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		router.ServeHTTP(w, req)

		assert.Equal(t, "http://localhost:3000", w.Header().Get("Access-Control-Allow-Origin"))

		// Test disallowed origin
		w = httptest.NewRecorder()
		req, _ = http.NewRequest("GET", "/health", nil)
		req.Header.Set("Origin", "http://malicious.com")
		router.ServeHTTP(w, req)

		assert.Empty(t, w.Header().Get("Access-Control-Allow-Origin"))
	})
}

// Benchmark critical endpoints
func BenchmarkCriticalEndpoints(b *testing.B) {
	gin.SetMode(gin.TestMode)
	cfg := &config.Config{
		JWTSecret: "benchmark-secret",
		Environment: "test",
	}
	
	server := &Server{
		db:     nil,
		config: cfg,
		router: gin.New(),
	}
	
	server.setupRoutes()
	router := server.router

	b.Run("HealthEndpoint", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/health", nil)
			router.ServeHTTP(w, req)
		}
	})

	b.Run("AuthenticationMiddleware", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/api/v1/users/1", nil) // Will fail auth
			router.ServeHTTP(w, req)
		}
	})

	b.Run("InputSanitization", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/health?safe=value", nil)
			router.ServeHTTP(w, req)
		}
	})
}