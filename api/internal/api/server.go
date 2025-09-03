package api

import (
	"database/sql"
	"net/http"

	"github.com/fowler013/sleepr/internal/config"
	"github.com/fowler013/sleepr/internal/handlers"
	"github.com/fowler013/sleepr/internal/middleware"
	"github.com/gin-gonic/gin"
	ginSwagger "github.com/swaggo/gin-swagger"
	swaggerFiles "github.com/swaggo/files"
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
	s.router.Use(middleware.RateLimit())

	// Health check (no validation needed)
	s.router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
			"version": "1.0.0",
			"environment": s.config.Environment,
		})
	})

	// Swagger documentation
	s.router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	// Public API routes (no authentication required)
	public := s.router.Group("/api/v1/public")
	public.Use(middleware.ValidateID())
	
	// Authentication routes
	auth := public.Group("/auth")
	auth.POST("/login", handlers.Login(s.db, s.config))
	
	// Public analytics (limited)
	publicAnalytics := public.Group("/analytics")
	publicAnalytics.GET("/waiver-wire", handlers.GetWaiverWireRecommendations(s.db))

	// Protected API routes (authentication required)
	api := s.router.Group("/api/v1")
	api.Use(middleware.ValidateID())
	api.Use(middleware.JWTAuth(s.config))
	
	// Token refresh endpoint
	api.POST("/auth/refresh", handlers.RefreshToken(s.config))
	
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
