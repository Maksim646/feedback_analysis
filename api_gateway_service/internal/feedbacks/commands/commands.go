package commands

import (
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/dto"
)

type FeedbackCommands struct {
	CreateFeedbackAnalysis CreateFeedbackAnalysisCmdHandler
}

func NewFeedbackCommands(createFeedbackAnalysis CreateFeedbackAnalysisCmdHandler) *FeedbackCommands {
	return &FeedbackCommands{CreateFeedbackAnalysis: createFeedbackAnalysis}
}

type CreateFeedbackAnalysisCommand struct {
	CreateDto *dto.CreateFeedbackAnalysisDto
}

func NewCreateFeedbackAnalysisCommand(createDto *dto.CreateFeedbackAnalysisDto) *CreateFeedbackAnalysisCommand {
	return &CreateFeedbackAnalysisCommand{CreateDto: createDto}
}
