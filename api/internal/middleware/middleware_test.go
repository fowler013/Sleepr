package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/fowler013/sleepr/internal/config"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"github.com/stretchr/testify/assert"
)

func setupTestMiddleware() (*gin.Engine, *config.Config) {
	gin.SetMode(gin.TestMode)
	cfg := &config.Config{
		JWTSecret: "test-secret-key-for-middleware-testing",
	}
	
	router := gin.New()
	return router, cfg
}

func generateValidJWT(secret string) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id":  123,
		"username": "testuser",
		"exp":      time.Now().Add(time.Hour).Unix(),
		"iat":      time.Now().Unix(),
	})
	
	return token.SignedString([]byte(secret))
}

func TestJWTAuthMiddleware(t *testing.T) {
	router, cfg := setupTestMiddleware()
	
	// Protected endpoint
	protected := router.Group("/protected")
	protected.Use(JWTAuth(cfg))
	protected.GET("/test", func(c *gin.Context) {
		userID, _ := c.Get("user_id")
		username, _ := c.Get("username")
		c.JSON(http.StatusOK, gin.H{
			"message":  "success",
			"user_id":  userID,
			"username": username,
		})
	})

	t.Run("NoAuthorizationHeader", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/protected/test", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("InvalidAuthorizationHeaderFormat", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/protected/test", nil)
		req.Header.Set("Authorization", "Invalid token format")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("ValidJWTToken", func(t *testing.T) {
		token, err := generateValidJWT(cfg.JWTSecret)
		assert.NoError(t, err)
		
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/protected/test", nil)
		req.Header.Set("Authorization", "Bearer "+token)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("InvalidJWTToken", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/protected/test", nil)
		req.Header.Set("Authorization", "Bearer invalid.jwt.token")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("ExpiredJWTToken", func(t *testing.T) {
		// Create an expired token
		expiredToken := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
			"user_id":  123,
			"username": "testuser",
			"exp":      time.Now().Add(-time.Hour).Unix(), // Expired 1 hour ago
			"iat":      time.Now().Add(-time.Hour * 2).Unix(),
		})
		
		tokenString, err := expiredToken.SignedString([]byte(cfg.JWTSecret))
		assert.NoError(t, err)
		
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/protected/test", nil)
		req.Header.Set("Authorization", "Bearer "+tokenString)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestRateLimitMiddleware(t *testing.T) {
	router, _ := setupTestMiddleware()
	
	router.Use(RateLimit())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	t.Run("WithinRateLimit", func(t *testing.T) {
		// Make a few requests, should all succeed
		for i := 0; i < 10; i++ {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/test", nil)
			router.ServeHTTP(w, req)
			
			assert.Equal(t, http.StatusOK, w.Code)
		}
	})

	t.Run("ExceedRateLimit", func(t *testing.T) {
		router2, _ := setupTestMiddleware()
		router2.Use(RateLimit())
		router2.GET("/test", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"message": "success"})
		})

		// Make many requests to exceed rate limit
		var lastStatusCode int
		for i := 0; i < 110; i++ {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", "/test", nil)
			router2.ServeHTTP(w, req)
			lastStatusCode = w.Code
		}
		
		// Last request should be rate limited
		assert.Equal(t, http.StatusTooManyRequests, lastStatusCode)
	})
}

func TestSanitizeInputMiddleware(t *testing.T) {
	router, _ := setupTestMiddleware()
	
	router.Use(SanitizeInput())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	t.Run("SafeInput", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test?name=john&age=25", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("DangerousSQLInjection", func(t *testing.T) {
		dangerousQueries := []string{
			"/test?q=%27%20OR%201%3D1--",                   // ' OR 1=1--
			"/test?q=%27%3B%20DROP%20TABLE%20users%3B%20--", // '; DROP TABLE users; --
			"/test?q=UNION%20SELECT%20*%20FROM%20passwords", // UNION SELECT * FROM passwords
			"/test?q=INSERT%20INTO%20users%20VALUES",        // INSERT INTO users VALUES
		}

		for _, query := range dangerousQueries {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", query, nil)
			router.ServeHTTP(w, req)
			
			assert.Equal(t, http.StatusBadRequest, w.Code, "Query should be rejected: %s", query)
		}
	})
}

func TestValidateIDMiddleware(t *testing.T) {
	router, _ := setupTestMiddleware()
	
	router.Use(ValidateID())
	router.GET("/users/:id", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	t.Run("ValidID", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/users/123", nil)
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("InvalidID", func(t *testing.T) {
		invalidIDs := []string{
			"/users/abc",
			"/users/-1",
			"/users/0",
			"/users/1.5",
		}

		for _, path := range invalidIDs {
			w := httptest.NewRecorder()
			req, _ := http.NewRequest("GET", path, nil)
			router.ServeHTTP(w, req)
			
			assert.Equal(t, http.StatusBadRequest, w.Code, "ID should be invalid: %s", path)
		}
	})
}

func TestCORSMiddleware(t *testing.T) {
	router, _ := setupTestMiddleware()
	
	router.Use(CORS())
	router.GET("/test", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"message": "success"})
	})

	t.Run("AllowedOrigin", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		assert.Equal(t, "http://localhost:3000", w.Header().Get("Access-Control-Allow-Origin"))
	})

	t.Run("DisallowedOrigin", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("GET", "/test", nil)
		req.Header.Set("Origin", "http://malicious-site.com")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
		assert.Empty(t, w.Header().Get("Access-Control-Allow-Origin"))
	})

	t.Run("OptionsRequest", func(t *testing.T) {
		w := httptest.NewRecorder()
		req, _ := http.NewRequest("OPTIONS", "/test", nil)
		req.Header.Set("Origin", "http://localhost:3000")
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusNoContent, w.Code)
		assert.Equal(t, "http://localhost:3000", w.Header().Get("Access-Control-Allow-Origin"))
	})
}