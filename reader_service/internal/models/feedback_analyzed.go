package models

import (
	// "github.com/Maksim646/feedback_analysis/pkg/utils"
	"time"

	readerService "github.com/Maksim646/feedback_analysis/reader_service/proto/feedback_reader"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type FeedbackAnalyzed struct {
	FeedbackID        string    `json:"feedback_id" validate:"required"`
	FeedbackSource    string    `json:"feedback_source" validate:"required"`
	Text              string    `json:"feedback_text" validate:"required,min=1,max=500"`
	Keywords          []string  `json:"keywords" validate:"required,min=1,max=500"`
	Sentiment         string    `json:"sentiment" validate:"required,min=1,max=255"`
	FeedbackTimestamp time.Time `json:"feedback_timestamp"`
}

// ProductsList products list response with pagination
// type ProductsList struct {
// 	TotalCount int64      `json:"totalCount" bson:"totalCount"`
// 	TotalPages int64      `json:"totalPages" bson:"totalPages"`
// 	Page       int64      `json:"page" bson:"page"`
// 	Size       int64      `json:"size" bson:"size"`
// 	HasMore    bool       `json:"hasMore" bson:"hasMore"`
// 	Products   []*Product `json:"products" bson:"products"`
// }

// func NewProductListWithPagination(products []*Product, count int64, pagination *utils.Pagination) *ProductsList {
// 	return &ProductsList{
// 		TotalCount: count,
// 		TotalPages: int64(pagination.GetTotalPages(int(count))),
// 		Page:       int64(pagination.GetPage()),
// 		Size:       int64(pagination.GetSize()),
// 		HasMore:    pagination.GetHasMore(int(count)),
// 		Products:   products,
// 	}
// }

func ProductToGrpcMessage(feedbackAnalyzed *FeedbackAnalyzed) *readerService.Feedback {
	return &readerService.Feedback{
		FeedbackID:        feedbackAnalyzed.FeedbackID,
		FeedbackSource:    feedbackAnalyzed.FeedbackSource,
		Text:              feedbackAnalyzed.Text,
		Keywords:          feedbackAnalyzed.Keywords,
		Sentiment:         feedbackAnalyzed.Sentiment,
		FeedbackTimestamp: timestamppb.New(feedbackAnalyzed.FeedbackTimestamp),
	}
}

// func ProductListToGrpc(products *ProductsList) *readerService.SearchRes {
// 	list := make([]*readerService.Product, 0, len(products.Products))
// 	for _, product := range products.Products {
// 		list = append(list, ProductToGrpcMessage(product))
// 	}

// 	return &readerService.SearchRes{
// 		TotalCount: products.TotalCount,
// 		TotalPages: products.TotalPages,
// 		Page:       products.Page,
// 		Size:       products.Size,
// 		HasMore:    products.HasMore,
// 		Products:   list,
// 	}
// }
