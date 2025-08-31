package commands

import (
	"context"

	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/reader_service/config"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/repository"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/models"
	"github.com/opentracing/opentracing-go"
)

type CreateFeedbackAnalyzedCmdHandler interface {
	Handle(ctx context.Context, command *FeedbackAnalyzedCommand) error
}

type createFeedbackAnalyzedHandler struct {
	log       logger.Logger
	cfg       *config.Config
	mongoRepo repository.Repository
	redisRepo repository.CacheRepository
}

func NewCreateFeedbackHandler(log logger.Logger, cfg *config.Config, mongoRepo repository.Repository, redisRepo repository.CacheRepository) *createFeedbackAnalyzedHandler {
	return &createFeedbackAnalyzedHandler{log: log, cfg: cfg, mongoRepo: mongoRepo, redisRepo: redisRepo}
}

func (c *createFeedbackAnalyzedHandler) Handle(ctx context.Context, command *FeedbackAnalyzedCommand) error {
	span, ctx := opentracing.StartSpanFromContext(ctx, "createFeedbackHandler.Handle")
	defer span.Finish()

	feedback_analyzed := &models.FeedbackAnalyzed{
		FeedbackID:        command.FeedbackID,
		FeedbackSource:    command.FeedbackSource,
		Text:              command.Text,
		Keywords:          command.Keywords,
		Sentiment:         command.Sentiment,
		FeedbackTimestamp: command.FeedbackTimestamp,
	}

	created, err := c.mongoRepo.CreateFeedback(ctx, feedback_analyzed)
	if err != nil {
		return err
	}

	c.redisRepo.PutFeedback(ctx, created.FeedbackID, created)
	return nil
}
