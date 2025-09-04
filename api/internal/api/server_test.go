package api

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/fowler013/sleepr/internal/config"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func setupTestRouter() *gin.Engine {
	gin.SetMode(gin.TestMode)
	cfg := &config.Config{
		JWTSecret: "test-secret-key",
		Environment: "test",
	}
	
	// For testing, we'll mock the database
	server := &Server{
		db:     nil, // Mock database would go here
		config: cfg,
		router: gin.New(),
	}
	
	server.setupRoutes()
	return server.router
}

func TestHealthEndpoint(t *testing.T) {
	router := setupTestRouter()
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/health", nil)
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusOK, w.Code)
	
	var response map[string]interface{}
	json.Unmarshal(w.Body.Bytes(), &response)
	assert.Equal(t, "ok", response["status"])
	assert.Equal(t, "1.0.0", response["version"])
}

func TestAuthenticationRequired(t *testing.T) {
	router := setupTestRouter()
	
	// Test that protected endpoints require authentication
	protectedEndpoints := []string{
		"/api/v1/users/1",
		"/api/v1/teams/",
		"/api/v1/players/1",
	}
	
	for _, endpoint := range protectedEndpoints {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", endpoint, nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code, "Endpoint %s should require authentication", endpoint)
	}
}

func TestCORSHeaders(t *testing.T) {
	router := setupTestRouter()
	
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("OPTIONS", "/health", nil)
	req.Header.Set("Origin", "http://localhost:3000")
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusNoContent, w.Code)
	assert.Equal(t, "http://localhost:3000", w.Header().Get("Access-Control-Allow-Origin"))
}

func TestRateLimit(t *testing.T) {
	router := setupTestRouter()
	
	// Make many requests to test rate limiting
	// Note: This is a basic test - in practice you'd want more sophisticated testing
	for i := 0; i < 105; i++ { // Exceed the 100 request limit
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/health", nil)
		router.ServeHTTP(w, req)
		
		if i >= 100 {
			assert.Equal(t, http.StatusTooManyRequests, w.Code, "Should be rate limited after 100 requests")
			break
		}
	}
}

func TestInputValidation(t *testing.T) {
	router := setupTestRouter()
	
	// Test invalid ID parameter
	w := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/api/v1/public/analytics/waiver-wire", nil)
	router.ServeHTTP(w, req)
	
	// Should not return 400 for this endpoint as it doesn't require ID
	assert.NotEqual(t, http.StatusBadRequest, w.Code)
	
	// Test with dangerous query parameter
	w = httptest.NewRecorder()
	req, _ = http.NewRequest("GET", "/health?search=%27%3B%20DROP%20TABLE%20users%3B%20--", nil) // URL encoded
	router.ServeHTTP(w, req)
	
	assert.Equal(t, http.StatusBadRequest, w.Code, "Should reject dangerous SQL injection patterns")
}

func TestPublicEndpoints(t *testing.T) {
	router := setupTestRouter()
	
	// Test that public endpoints don't require authentication
	// Note: Only testing endpoints that don't require database access in this test
	publicEndpoints := map[string]string{
		"/api/v1/public/analytics/waiver-wire": "GET",
		// Skipping login endpoint due to database dependency in test environment
	}
	
	for endpoint, method := range publicEndpoints {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest(method, endpoint, nil)
		router.ServeHTTP(w, req)
		
		// Should not be unauthorized (might be other errors like missing DB)
		// We're mainly checking that JWT authentication is not required
		assert.NotEqual(t, http.StatusUnauthorized, w.Code, "Public endpoint %s should not require auth", endpoint)
	}
	
	// Test login endpoint separately with expectation of database error
	t.Run("LoginEndpointAuthenticationNotRequired", func(t *testing.T) {
		// This test may cause a panic due to nil database, so we'll skip it for now
		// In a real implementation, we'd use database mocking
		t.Skip("Skipping login endpoint test due to database dependency")
	})
}

// Benchmark tests
func BenchmarkHealthEndpoint(b *testing.B) {
	router := setupTestRouter()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/health", nil)
		router.ServeHTTP(w, req)
	}
}

func BenchmarkAuthenticationMiddleware(b *testing.B) {
	router := setupTestRouter()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/api/v1/users/1", nil)
		router.ServeHTTP(w, req)
	}
}
