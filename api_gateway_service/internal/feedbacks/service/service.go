package service

import (
	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/feedbacks/commands"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/feedbacks/queries"
	kafkaClient "github.com/Maksim646/feedback_analysis/pkg/kafka"
	"github.com/Maksim646/feedback_analysis/pkg/logger"
	readerService "github.com/Maksim646/feedback_analysis/reader_service/proto/feedback_reader"
)

type FeedbackService struct {
	Commands *commands.FeedbackCommands
	Queries  *queries.FeedbackQueries
}

func NewFeedbackService(log logger.Logger, cfg *config.Config, kafkaProducer kafkaClient.Producer, rsClient readerService.FeedbackReaderClient) *FeedbackService {

	createFeedbackHandler := commands.NewCreateFeedbackAnalysisHandler(log, cfg, kafkaProducer)

	getFeedbackByIdHandler := queries.NewGetFeedbackByIdHandler(log, cfg, rsClient)
	// searchFeedbackHandler := queries.NewSearchFeedbackHandler(log, cfg, rsClient)

	feedbackCommands := commands.NewFeedbackCommands(createFeedbackHandler)
	feedbackQueries := queries.NewFeedbackQueries(getFeedbackByIdHandler /*, searchFeedbackHandler*/)

	return &FeedbackService{Commands: feedbackCommands, Queries: feedbackQueries}
}
