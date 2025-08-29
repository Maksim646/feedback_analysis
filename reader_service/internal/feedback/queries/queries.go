package queries

import (
	uuid "github.com/satori/go.uuid"
)

type FeedbackQueries struct {
	GetFeedbackById GetFeedbackByIdHandler
	// SearchProduct   SearchProductHandler
}

func NewFeedbackQueries(getFeedbackById GetFeedbackByIdHandler) *FeedbackQueries { //, searchProduct SearchProductHandler
	return &FeedbackQueries{GetFeedbackById: getFeedbackById} //, SearchProduct: searchProduct
}

type GetFeedbackByIdQuery struct {
	FeedbackID uuid.UUID `json:"feedbackId" bson:"_id,omitempty"`
}

func NewGetFeedbackByIdQuery(feedbackID uuid.UUID) *GetFeedbackByIdQuery {
	return &GetFeedbackByIdQuery{FeedbackID: feedbackID}
}

// type SearchProductQuery struct {
// 	Text       string            `json:"text"`
// 	Pagination *utils.Pagination `json:"pagination"`
// }

// func NewSearchProductQuery(text string, pagination *utils.Pagination) *SearchProductQuery {
// 	return &SearchProductQuery{Text: text, Pagination: pagination}
// }
