package v1

import (
	"net/http"

	"github.com/labstack/echo/v4"
)

func (h *feedbacksHandlers)  MapRoutes() {
	h.group.POST("", h.CreateFeedback())
	h.group.GET("/:id", h.GetFeedbackByID())
	h.group.GET("/search", h.SearchFeedback())
	h.group.Any("/health", func(c echo.Context) error {
		return c.JSON(http.StatusOK, "OK")
	})
}
