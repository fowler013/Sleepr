package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// ErrorResponse represents a standardized error response
type ErrorResponse struct {
	Error   string      `json:"error"`
	Code    string      `json:"code,omitempty"`
	Details interface{} `json:"details,omitempty"`
}

// SuccessResponse represents a standardized success response
type SuccessResponse struct {
	Data    interface{} `json:"data"`
	Message string      `json:"message,omitempty"`
}

// HandleError sends a standardized error response
func HandleError(c *gin.Context, statusCode int, err error, code string) {
	response := ErrorResponse{
		Error: err.Error(),
		Code:  code,
	}
	c.JSON(statusCode, response)
}

// HandleValidationError sends a validation error response
func HandleValidationError(c *gin.Context, err error) {
	response := ErrorResponse{
		Error:   "Validation failed",
		Code:    "VALIDATION_ERROR",
		Details: err.Error(),
	}
	c.JSON(http.StatusBadRequest, response)
}

// HandleSuccess sends a standardized success response
func HandleSuccess(c *gin.Context, data interface{}, message string) {
	response := SuccessResponse{
		Data:    data,
		Message: message,
	}
	c.JSON(http.StatusOK, response)
}

// HandleCreated sends a standardized created response
func HandleCreated(c *gin.Context, data interface{}, message string) {
	response := SuccessResponse{
		Data:    data,
		Message: message,
	}
	c.JSON(http.StatusCreated, response)
}
