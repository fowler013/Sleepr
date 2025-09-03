package handlers

import (
	"database/sql"
	"net/http"
	"strconv"

	"github.com/fowler013/sleepr/internal/config"
	"github.com/fowler013/sleepr/internal/models"
	"github.com/fowler013/sleepr/internal/services"
	"github.com/gin-gonic/gin"
)

// CreateUser creates a new user
func CreateUser(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		var user models.User
		if err := c.ShouldBindJSON(&user); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
			return
		}

		userService := services.NewUserService(db)
		if err := userService.Create(&user); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusCreated, user)
	}
}

// GetUser retrieves a user by ID
func GetUser(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
			return
		}

		userService := services.NewUserService(db)
		user, err := userService.GetByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
			return
		}

		c.JSON(http.StatusOK, user)
	}
}

// GetTeams retrieves all teams for a user
func GetTeams(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		teamService := services.NewTeamService(db)
		teams, err := teamService.GetAll()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, teams)
	}
}

// GetTeam retrieves a specific team
func GetTeam(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid team ID"})
			return
		}

		teamService := services.NewTeamService(db)
		team, err := teamService.GetByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Team not found"})
			return
		}

		c.JSON(http.StatusOK, team)
	}
}

// SyncTeamFromSleeper syncs team data from Sleeper API
func SyncTeamFromSleeper(db *sql.DB, cfg *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		teamID := c.Param("id")

		sleeperService := services.NewSleeperService(cfg.SleeperAPIURL)
		teamService := services.NewTeamService(db)

		if err := teamService.SyncFromSleeper(teamID, sleeperService); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{"message": "Team synced successfully"})
	}
}

// GetPlayers retrieves all players
func GetPlayers(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		playerService := services.NewPlayerService(db)
		players, err := playerService.GetAll()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, players)
	}
}

// GetPlayer retrieves a specific player
func GetPlayer(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid player ID"})
			return
		}

		playerService := services.NewPlayerService(db)
		player, err := playerService.GetByID(id)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Player not found"})
			return
		}

		c.JSON(http.StatusOK, player)
	}
}

// GetPlayerStats retrieves player statistics
func GetPlayerStats(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid player ID"})
			return
		}

		playerService := services.NewPlayerService(db)
		stats, err := playerService.GetStats(id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, stats)
	}
}

// GetTeamRecommendations provides team improvement recommendations
func GetTeamRecommendations(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid team ID"})
			return
		}

		analyticsService := services.NewAnalyticsService(db)
		recommendations, err := analyticsService.GetTeamRecommendations(id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, recommendations)
	}
}

// GetPlayerProjection provides player performance projections
func GetPlayerProjection(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		id, err := strconv.Atoi(c.Param("id"))
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid player ID"})
			return
		}

		analyticsService := services.NewAnalyticsService(db)
		projection, err := analyticsService.GetPlayerProjection(id)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, projection)
	}
}

// GetWaiverWireRecommendations provides waiver wire pickup recommendations
func GetWaiverWireRecommendations(db *sql.DB) gin.HandlerFunc {
	return func(c *gin.Context) {
		analyticsService := services.NewAnalyticsService(db)
		recommendations, err := analyticsService.GetWaiverWireRecommendations()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, recommendations)
	}
}
