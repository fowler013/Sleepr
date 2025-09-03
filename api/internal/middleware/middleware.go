package middleware

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// CORS middleware for handling Cross-Origin Resource Sharing
func CORS() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// Only allow specific origins in production
		origin := c.Request.Header.Get("Origin")
		allowedOrigins := []string{
			"http://localhost:3000",
			"http://localhost:8080",
			"http://127.0.0.1:3000",
			"http://127.0.0.1:8080",
		}

		// In development, allow localhost origins
		allowed := false
		for _, allowedOrigin := range allowedOrigins {
			if origin == allowedOrigin {
				allowed = true
				break
			}
		}

		if allowed {
			c.Writer.Header().Set("Access-Control-Allow-Origin", origin)
		}

		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	})
}

// Logger middleware for request logging
func Logger() gin.HandlerFunc {
	return gin.LoggerWithFormatter(func(param gin.LogFormatterParams) string {
		return fmt.Sprintf("%s - [%s] \"%s %s %s %d %s \"%s\" %s\"\n",
			param.ClientIP,
			param.TimeStamp.Format(time.RFC1123),
			param.Method,
			param.Path,
			param.Request.Proto,
			param.StatusCode,
			param.Latency,
			param.Request.UserAgent(),
			param.ErrorMessage,
		)
	})
}

// ValidateID middleware validates that ID parameters are positive integers
func ValidateID() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// Check all ID parameters
		params := []string{"id", "user_id", "team_id", "player_id"}
		for _, param := range params {
			if idStr := c.Param(param); idStr != "" {
				if id, err := strconv.Atoi(idStr); err != nil || id <= 0 {
					c.JSON(http.StatusBadRequest, gin.H{
						"error": fmt.Sprintf("Invalid %s: must be a positive integer", param),
					})
					c.Abort()
					return
				}
			}
		}
		c.Next()
	})
}

// SanitizeInput middleware sanitizes string inputs
func SanitizeInput() gin.HandlerFunc {
	return gin.HandlerFunc(func(c *gin.Context) {
		// Prevent SQL injection patterns in query parameters
		for key, values := range c.Request.URL.Query() {
			for _, value := range values {
				// Check for common SQL injection patterns
				dangerous := []string{"'", "\"", ";", "--", "/*", "*/", "xp_", "sp_", "exec", "execute", "union", "select", "insert", "update", "delete", "drop", "create", "alter"}
				lowerValue := strings.ToLower(value)
				for _, pattern := range dangerous {
					if strings.Contains(lowerValue, pattern) {
						c.JSON(http.StatusBadRequest, gin.H{
							"error": fmt.Sprintf("Invalid characters in parameter %s", key),
						})
						c.Abort()
						return
					}
				}
			}
		}
		c.Next()
	})
}
