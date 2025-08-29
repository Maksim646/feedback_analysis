package commands

import (
	"time"
)

type FeedbackAnalyzedCommands struct {
	CreateFeedbackAnalyzed CreateFeedbackAnalyzedCmdHandler
}

func NewFeedbackAnalyzedCommands(
	createFeedbackAnalyzed CreateFeedbackAnalyzedCmdHandler,
) *FeedbackAnalyzedCommands {
	return &FeedbackAnalyzedCommands{CreateFeedbackAnalyzed: createFeedbackAnalyzed}
}

type FeedbackAnalyzedCommand struct {
	FeedbackID        string    `json:"feedback_id" validate:"required"`
	FeedbackSource    string    `json:"feedback_source" validate:"required"`
	Text              string    `json:"feedback_text" validate:"required,min=1,max=500"`
	Keywords          []string  `json:"keywords" validate:"required,min=1,max=500"`
	Sentiment         string    `json:"sentiment" validate:"required,min=1,max=255"`
	FeedbackTimestamp time.Time `json:"feedback_timestamp"`
}

func NewFeedbackAnalyzedCommand(feedbackID string, text string, feedbackSource string, keywords []string, sentiment string, feedbackTimestamp time.Time) *FeedbackAnalyzedCommand {
	return &FeedbackAnalyzedCommand{FeedbackID: feedbackID, Text: text, FeedbackSource: feedbackSource, Keywords: keywords, Sentiment: sentiment, FeedbackTimestamp: feedbackTimestamp}
}

// type UpdateProductCommand struct {
// 	ProductID   string    `json:"productId" bson:"_id,omitempty"`
// 	Name        string    `json:"name,omitempty" bson:"name,omitempty" validate:"required,min=3,max=250"`
// 	Description string    `json:"description,omitempty" bson:"description,omitempty" validate:"required,min=3,max=500"`
// 	Price       float64   `json:"price,omitempty" bson:"price,omitempty" validate:"required"`
// 	UpdatedAt   time.Time `json:"updatedAt,omitempty" bson:"updatedAt,omitempty"`
// }

// func NewUpdateProductCommand(productID string, name string, description string, price float64, updatedAt time.Time) *UpdateProductCommand {
// 	return &UpdateProductCommand{ProductID: productID, Name: name, Description: description, Price: price, UpdatedAt: updatedAt}
// }

// type DeleteProductCommand struct {
// 	ProductID uuid.UUID `json:"productId" bson:"_id,omitempty"`
// }

// func NewDeleteProductCommand(productID uuid.UUID) *DeleteProductCommand {
// 	return &DeleteProductCommand{ProductID: productID}
// }
