package dto

import uuid "github.com/satori/go.uuid"

type CreateFeedbackAnalysisDto struct {
	FeedbackID        uuid.UUID `json:"feedback_id" validate:"required"`
	FeedbackSource    string    `json:"feedback_source" validate:"required"`
	Text              string    `json:"feedback_text" validate:"required,min=1,max=500"`
	FeedbackTimestamp int64     `json:"feedback_timestamp"`
}

type CreateFeedbackAnalysisResponseDto struct {
	FeedbackID uuid.UUID `json:"feedback_id" validate:"required"`
}
