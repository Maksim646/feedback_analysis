package dto

import (
	readerService "github.com/Maksim646/feedback_analysis/proto/feedback_reader"
)

type FeedbackResponseDto struct {
	FeedbackID        string   `json:"feedback_id" validate:"required"`
	FeedbackSource    string   `json:"feedback_source" validate:"required"`
	Text              string   `json:"feedback_text" validate:"required,min=1,max=500"`
	Keywords          []string `json:"keywords" validate:"required,min=1,max=500"`
	Sentiment         string   `json:"sentiment" validate:"required,min=1,max=255"`
	FeedbackTimestamp int64    `json:"feedback_timestamp"`
}

func FeedbackResponseFromGrpc(feedback *readerService.Feedback) *FeedbackResponseDto {
	return &FeedbackResponseDto{
		FeedbackID:        feedback.GetFeedbackID(),
		FeedbackSource:    feedback.GetFeedbackSource(),
		Text:              feedback.GetText(),
		Keywords:          feedback.GetKeywords(),
		Sentiment:         feedback.GetSentiment(),
		FeedbackTimestamp: feedback.GetFeedbackTimestamp().AsTime().Unix(),
	}
}
