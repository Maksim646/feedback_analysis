package queries

import (
	"context"

	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/reader_service/config"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/repository"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/models"
	"github.com/opentracing/opentracing-go"
)

type GetFeedbackByIdHandler interface {
	Handle(ctx context.Context, query *GetFeedbackByIdQuery) (*models.FeedbackAnalyzed, error)
}

type getFeedbackByIdHandler struct {
	log       logger.Logger
	cfg       *config.Config
	mongoRepo repository.Repository
	redisRepo repository.CacheRepository
}

func NewGetFeedbackByIdHandler(log logger.Logger, cfg *config.Config, mongoRepo repository.Repository, redisRepo repository.CacheRepository) *getFeedbackByIdHandler {
	return &getFeedbackByIdHandler{log: log, cfg: cfg, mongoRepo: mongoRepo, redisRepo: redisRepo}
}

func (q *getFeedbackByIdHandler) Handle(ctx context.Context, query *GetFeedbackByIdQuery) (*models.FeedbackAnalyzed, error) {
	span, ctx := opentracing.StartSpanFromContext(ctx, "getFeedbackByIdHandler.Handle")
	defer span.Finish()

	if feedback, err := q.redisRepo.GetFeedbackAnalyzed(ctx, query.FeedbackID.String()); err == nil && feedback != nil {
		return feedback, nil
	}

	feedback, err := q.mongoRepo.GetFeedbackById(ctx, query.FeedbackID)
	if err != nil {
		return nil, err
	}

	q.redisRepo.PutFeedbackAnalyzed(ctx, feedback.FeedbackID, feedback)
	return feedback, nil
}
