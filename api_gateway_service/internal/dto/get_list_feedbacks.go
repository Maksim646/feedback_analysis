package dto

import readerService "github.com/Maksim646/feedback_analysis/proto/feedback_reader"

type FeedbacksListResponse struct {
	TotalCount int64                  `json:"totalCount" bson:"totalCount"`
	TotalPages int64                  `json:"totalPages" bson:"totalPages"`
	Page       int64                  `json:"page" bson:"page"`
	Size       int64                  `json:"size" bson:"size"`
	HasMore    bool                   `json:"hasMore" bson:"hasMore"`
	Feedbacks  []*FeedbackResponseDto `json:"feedbacks" bson:"feedbacks"`
}

func FeedbacksListResponseFromGrpc(listResponse *readerService.SearchRes) *FeedbacksListResponse {
	list := make([]*FeedbackResponseDto, 0, len(listResponse.GetFeedbacks()))
	for _, feedback := range listResponse.GetFeedbacks() {
		list = append(list, FeedbackResponseFromGrpc(feedback))
	}

	return &FeedbacksListResponse{
		TotalCount: listResponse.GetTotalCount(),
		TotalPages: listResponse.GetTotalPages(),
		Page:       listResponse.GetPage(),
		Size:       listResponse.GetSize(),
		HasMore:    listResponse.GetHasMore(),
		Feedbacks:  list,
	}
}
