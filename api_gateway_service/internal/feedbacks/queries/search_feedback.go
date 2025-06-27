package queries

import (
	"context"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"
	"github.com/Maksim646/feedback_analysis/api_gateway_service/internal/dto"
	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/pkg/tracing"
	readerService "github.com/Maksim646/feedback_analysis/proto/feedback_reader"
	"github.com/opentracing/opentracing-go"
)

type SearchFeedbackHandler interface {
	Handle(ctx context.Context, query *SearchFeedbackQuery) (*dto.FeedbacksListResponse, error)
}

type searchFeedbackHandler struct {
	log      logger.Logger
	cfg      *config.Config
	rsClient readerService.FeedbackReaderClient
}

func NewSearchFeedbackHandler(log logger.Logger, cfg *config.Config, rsClient readerService.FeedbackReaderClient) *searchFeedbackHandler {
	return &searchFeedbackHandler{log: log, cfg: cfg, rsClient: rsClient}
}

func (s *searchFeedbackHandler) Handle(ctx context.Context, query *SearchFeedbackQuery) (*dto.FeedbacksListResponse, error) {
	span, ctx := opentracing.StartSpanFromContext(ctx, "searchFeedbackHandler.Handle")
	defer span.Finish()

	ctx = tracing.InjectTextMapCarrierToGrpcMetaData(ctx, span.Context())
	res, err := s.rsClient.SearchFeedback(ctx, &readerService.SearchReq{
		Search: query.Text,
		Page:   int64(query.Pagination.GetPage()),
		Size:   int64(query.Pagination.GetSize()),
	})
	if err != nil {
		return nil, err
	}

	return dto.FeedbacksListResponseFromGrpc(res), nil
}
