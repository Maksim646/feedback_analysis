package service

import (
	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/reader_service/config"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/commands"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/queries"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/repository"
)

type FeedbackService struct {
	Commands *commands.FeedbackAnalyzedCommands
	Queries  *queries.FeedbackQueries
}

func NewFeedbackService(
	log logger.Logger,
	cfg *config.Config,
	mongoRepo repository.Repository,
	redisRepo repository.CacheRepository,
) *FeedbackService {

	createProductHandler := commands.NewCreateFeedbackHandler(log, cfg, mongoRepo, redisRepo)
	// deleteProductCmdHandler := commands.NewDeleteProductCmdHandler(log, cfg, mongoRepo, redisRepo)
	// updateProductCmdHandler := commands.NewUpdateProductCmdHandler(log, cfg, mongoRepo, redisRepo)

	getProductByIdHandler := queries.NewGetFeedbackByIdHandler(log, cfg, mongoRepo, redisRepo)
	// searchProductHandler := queries.NewSearchProductHandler(log, cfg, mongoRepo, redisRepo)

	feedbackCommands := commands.NewFeedbackAnalyzedCommands(createProductHandler) //, updateProductCmdHandler, deleteProductCmdHandler
	feedbackQueries := queries.NewFeedbackQueries(getProductByIdHandler)           //, searchProductHandler

	return &FeedbackService{Commands: feedbackCommands, Queries: feedbackQueries}
}
