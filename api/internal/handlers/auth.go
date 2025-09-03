package handlers

import (
	"database/sql"
	"net/http"
	"time"

	"github.com/fowler013/sleepr/internal/config"
	"github.com/fowler013/sleepr/internal/models"
	"github.com/fowler013/sleepr/internal/services"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

// LoginRequest represents a login request
type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	SleeperID string `json:"sleeper_id" binding:"required"`
}

// LoginResponse represents a login response
type LoginResponse struct {
	Token string      `json:"token"`
	User  models.User `json:"user"`
}

// Login authenticates a user and returns a JWT token
//
//	@Summary		User login
//	@Description	Authenticate user with Sleeper credentials and get JWT token
//	@Tags			authentication
//	@Accept			json
//	@Produce		json
//	@Param			request	body		LoginRequest	true	"Login credentials"
//	@Success		200		{object}	LoginResponse	"Successfully authenticated"
//	@Failure		400		{object}	handlers.ErrorResponse	"Invalid request"
//	@Failure		500		{object}	handlers.ErrorResponse	"Internal server error"
//	@Router			/public/auth/login [post]
func Login(db *sql.DB, cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		var req LoginRequest
		if err := c.ShouldBindJSON(&req); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": "Invalid request format",
				"details": err.Error(),
			})
			return
		}

		userService := services.NewUserService(db)
		user, err := userService.GetBySleeperID(req.SleeperID)
		if err != nil {
			// If user doesn't exist, create a new one
			user = &models.User{
				SleeperID:   req.SleeperID,
				Username:    req.Username,
				DisplayName: req.Username,
			}
			
			if err := userService.Create(user); err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{
					"error": "Failed to create user",
				})
				return
			}
		}

		// Generate JWT token
		token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
			"user_id":    user.ID,
			"username":   user.Username,
			"sleeper_id": user.SleeperID,
			"exp":        time.Now().Add(time.Hour * 24 * 7).Unix(), // 7 days
			"iat":        time.Now().Unix(),
		})

		tokenString, err := token.SignedString([]byte(cfg.JWTSecret))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Failed to generate token",
			})
			return
		}

		c.JSON(http.StatusOK, LoginResponse{
			Token: tokenString,
			User:  *user,
		})
	}
}

// RefreshToken refreshes an existing JWT token
func RefreshToken(cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get user info from context (set by JWT middleware)
		userID, exists := c.Get("user_id")
		if !exists {
			c.JSON(http.StatusUnauthorized, gin.H{
				"error": "Invalid token context",
			})
			return
		}

		username, _ := c.Get("username")

		// Generate new token
		token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
			"user_id":  userID,
			"username": username,
			"exp":      time.Now().Add(time.Hour * 24 * 7).Unix(), // 7 days
			"iat":      time.Now().Unix(),
		})

		tokenString, err := token.SignedString([]byte(cfg.JWTSecret))
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Failed to generate token",
			})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"token": tokenString,
		})
	}
}
