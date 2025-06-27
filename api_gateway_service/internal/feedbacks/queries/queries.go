package queries

import (
	"github.com/Maksim646/feedback_analysis/pkg/utils"
	uuid "github.com/satori/go.uuid"
)

type FeedbackQueries struct {
	GetFeedbackById GetFeedbackByIdHandler
	SearchFeedback  SearchFeedbackHandler
}

func NewFeedbackQueries(getFeedbackById GetFeedbackByIdHandler, searchFeedback SearchFeedbackHandler) *FeedbackQueries {
	return &FeedbackQueries{GetFeedbackById: getFeedbackById, SearchFeedback: searchFeedback}
}

type GetFeedbackByIdQuery struct {
	FeedbackID uuid.UUID `json:"feedbackId" validate:"required,gte=0,lte=255"`
}

func NewGetFeedbackByIdQuery(feedbackID uuid.UUID) *GetFeedbackByIdQuery {
	return &GetFeedbackByIdQuery{FeedbackID: feedbackID}
}

type SearchFeedbackQuery struct {
	Text       string            `json:"text"`
	Pagination *utils.Pagination `json:"pagination"`
}

func NewSearchFeedbackQuery(text string, pagination *utils.Pagination) *SearchFeedbackQuery {
	return &SearchFeedbackQuery{Text: text, Pagination: pagination}
}
