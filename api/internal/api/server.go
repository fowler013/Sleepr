package api

import (
	"database/sql"
	"net/http"

	"github.com/fowler013/sleepr/internal/config"
	"github.com/fowler013/sleepr/internal/handlers"
	"github.com/fowler013/sleepr/internal/middleware"
	"github.com/gin-gonic/gin"
)

// Server represents the API server
type Server struct {
	db     *sql.DB
	config *config.Config
	router *gin.Engine
}

// NewServer creates a new API server instance
func NewServer(db *sql.DB, cfg *config.Config) *Server {
	server := &Server{
		db:     db,
		config: cfg,
		router: gin.Default(),
	}

	server.setupRoutes()
	return server
}

// setupRoutes configures all API routes
func (s *Server) setupRoutes() {
	// Global middleware
	s.router.Use(middleware.CORS())
	s.router.Use(middleware.Logger())
	s.router.Use(middleware.SanitizeInput())

	// Health check (no validation needed)
	s.router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok"})
	})

	// API routes with ID validation
	api := s.router.Group("/api/v1")
	api.Use(middleware.ValidateID())
	
	// User routes
	users := api.Group("/users")
	users.POST("/", handlers.CreateUser(s.db))
	users.GET("/:id", handlers.GetUser(s.db))
	
	// Team routes
	teams := api.Group("/teams")
	teams.GET("/", handlers.GetTeams(s.db))
	teams.GET("/:id", handlers.GetTeam(s.db))
	teams.POST("/:id/sync", handlers.SyncTeamFromSleeper(s.db, s.config))
	
	// Player routes
	players := api.Group("/players")
	players.GET("/", handlers.GetPlayers(s.db))
	players.GET("/:id", handlers.GetPlayer(s.db))
	players.GET("/:id/stats", handlers.GetPlayerStats(s.db))
	
	// Analytics routes
	analytics := api.Group("/analytics")
	analytics.GET("/teams/:id/recommendations", handlers.GetTeamRecommendations(s.db))
	analytics.GET("/players/:id/projection", handlers.GetPlayerProjection(s.db))
	analytics.GET("/waiver-wire", handlers.GetWaiverWireRecommendations(s.db))
}

// Run starts the HTTP server
func (s *Server) Run(addr string) error {
	return s.router.Run(addr)
}
