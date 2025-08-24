package v1

import (
	"fmt"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/dto"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/metrics"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/middlewares"

	"net/http"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/feedbacks/commands"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/feedbacks/queries"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/feedbacks/service"
	"github.com/Maksim646/feedback_analysis/pkg/constants"
	httpErrors "github.com/Maksim646/feedback_analysis/pkg/http_errors"
	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/pkg/tracing"
	"github.com/Maksim646/feedback_analysis/pkg/utils"
	"github.com/go-playground/validator"
	"github.com/labstack/echo/v4"
	"github.com/opentracing/opentracing-go"
	uuid "github.com/satori/go.uuid"
)

type feedbacksHandlers struct {
	group   *echo.Group
	log     logger.Logger
	mw      middlewares.MiddlewareManager
	cfg     *config.Config
	ps      *service.FeedbackService
	v       *validator.Validate
	metrics *metrics.ApiGatewayMetrics
}

func NewFeedbacksHandlers(
	group *echo.Group,
	log logger.Logger,
	mw middlewares.MiddlewareManager,
	cfg *config.Config,
	ps *service.FeedbackService,
	v *validator.Validate,
	metrics *metrics.ApiGatewayMetrics,
) *feedbacksHandlers {
	return &feedbacksHandlers{group: group, log: log, mw: mw, cfg: cfg, ps: ps, v: v, metrics: metrics}
}

// AddFeedback
// @Summary Add new feedback
// @Description Add new feedback for analysis
// @Tags Feedbacks
// @Accept json
// @Produce json
// @Param feedback body dto.CreateFeedbackAnalysisDto true "Feedback input data"
// @Success 201 {object} dto.CreateFeedbackAnalysisResponseDto
// @Router /feedbacks [post]
func (h *feedbacksHandlers) CreateFeedback() echo.HandlerFunc {
	return func(c echo.Context) error {
		h.metrics.PostFeedbackRequests.Inc()

		ctx, span := tracing.StartHttpServerTracerSpan(c, "feedbacksHandlers.CreateFeedback")
		defer span.Finish()

		createDto := &dto.CreateFeedbackAnalysisDto{}
		if err := c.Bind(createDto); err != nil {
			h.log.WarnMsg("Bind", err)
			h.traceErr(span, err)
			return httpErrors.ErrorCtxResponse(c, err, h.cfg.Http.DebugErrorsResponse)
		}

		createDto.FeedbackID = uuid.NewV4()
		if err := h.v.StructCtx(ctx, createDto); err != nil {
			h.log.WarnMsg("validate", err)
			h.traceErr(span, err)
			return httpErrors.ErrorCtxResponse(c, err, h.cfg.Http.DebugErrorsResponse)
		}

		if err := h.ps.Commands.CreateFeedbackAnalysis.Handle(ctx, commands.NewCreateFeedbackAnalysisCommand(createDto)); err != nil {
			h.log.WarnMsg("CreateFeedback", err)
			h.metrics.ErrorHttpRequests.Inc()
			return httpErrors.ErrorCtxResponse(c, err, h.cfg.Http.DebugErrorsResponse)
		}

		h.metrics.SuccessHttpRequests.Inc()
		return c.JSON(http.StatusCreated, dto.CreateFeedbackAnalysisResponseDto{FeedbackID: createDto.FeedbackID})
	}
}

// GetFeedbackById
// @Summary Get feedback by ID
// @Description Get analyzed feedback by ID
// @Tags Feedbacks
// @Accept json
// @Produce json
// @Param id path string true "Feedback ID"
// @Success 200 {object} dto.FeedbackResponseDto
// @Failure 400 {object} dto.ErrorResponse "Invalid ID format"
// @Failure 404 {object} dto.ErrorResponse "Feedback not found"
// @Failure 500 {object} dto.ErrorResponse "Internal server error"
// @Router /feedbacks/{id} [get]
func (h *feedbacksHandlers) GetFeedbackByID() echo.HandlerFunc {
	return func(c echo.Context) error {
		h.metrics.GetFeedbackRequests.Inc()

		ctx, span := tracing.StartHttpServerTracerSpan(c, "feedbacksHandlers.GetFeedbackByID")
		defer span.Finish()

		feedbackUUID, err := uuid.FromString(c.Param(constants.ID))
		if err != nil {
			h.log.WarnMsg("uuid.FromString", err)
			h.traceErr(span, err)
			return httpErrors.ErrorCtxResponse(c, err, h.cfg.Http.DebugErrorsResponse)
		}

		fmt.Println("ВОТ ТАКОЙ ID feedbackUUID", feedbackUUID)

		query := queries.NewGetFeedbackByIdQuery(feedbackUUID)
		fmt.Println("ВСЕ ЕЩЕ НЕ УПАЛ")
		response, err := h.ps.Queries.GetFeedbackById.Handle(ctx, query)
		if err != nil {
			h.log.WarnMsg("GetFeedbackById", err)
			h.metrics.ErrorHttpRequests.Inc()
			return httpErrors.ErrorCtxResponse(c, err, h.cfg.Http.DebugErrorsResponse)
		}

		h.metrics.SuccessHttpRequests.Inc()
		return c.JSON(http.StatusOK, response)
	}
}

// SearchFeedback
// @Summary Search feedbacks
// @Description Search feedbacks by source, keywords or text with pagination
// @Tags Feedbacks
// @Accept json
// @Produce json
// @Param source query string false "Filter by feedback source (e.g., 'telegram', 'email')"
// @Param keywords query string false "Filter by comma-separated keywords"
// @Param text query string false "Search in feedback text"
// @Param page query int false "Page number (starts from 1)"
// @Param size query int false "Page size (number of items per page)"
// @Success 200 {object} dto.FeedbacksListResponse
// @Failure 400 {object} dto.ErrorResponse
// @Failure 500 {object} dto.ErrorResponse
// @Router /feedback/search [get]
func (h *feedbacksHandlers) SearchFeedback() echo.HandlerFunc {
	return func(c echo.Context) error {
		h.metrics.SearchFeedbackRequests.Inc()

		ctx, span := tracing.StartHttpServerTracerSpan(c, "feedbacksHandlers.SearchFeedback")
		defer span.Finish()

		pq := utils.NewPaginationFromQueryParams(c.QueryParam(constants.Size), c.QueryParam(constants.Page))

		query := queries.NewSearchFeedbackQuery(c.QueryParam(constants.Search), pq)
		response, err := h.ps.Queries.SearchFeedback.Handle(ctx, query)
		if err != nil {
			h.log.WarnMsg("SearchFeedback", err)
			h.metrics.ErrorHttpRequests.Inc()
			return httpErrors.ErrorCtxResponse(c, err, h.cfg.Http.DebugErrorsResponse)
		}

		h.metrics.SuccessHttpRequests.Inc()
		return c.JSON(http.StatusOK, response)
	}
}

func (h *feedbacksHandlers) traceErr(span opentracing.Span, err error) {
	span.SetTag("error", true)
	span.LogKV("error_code", err.Error())
	h.metrics.ErrorHttpRequests.Inc()
}
