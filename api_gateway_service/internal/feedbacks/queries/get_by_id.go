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

type GetFeedbackByIdHandler interface {
	Handle(ctx context.Context, query *GetFeedbackByIdQuery) (*dto.FeedbackResponseDto, error)
}

type getFeedbackByIdHandler struct {
	log      logger.Logger
	cfg      *config.Config
	rsClient readerService.FeedbackReaderClient
}

func NewGetFeedbackByIdHandler(log logger.Logger, cfg *config.Config, rsClient readerService.FeedbackReaderClient) *getFeedbackByIdHandler {
	return &getFeedbackByIdHandler{log: log, cfg: cfg, rsClient: rsClient}
}

func (q *getFeedbackByIdHandler) Handle(ctx context.Context, query *GetFeedbackByIdQuery) (*dto.FeedbackResponseDto, error) {
	span, ctx := opentracing.StartSpanFromContext(ctx, "getFeedbackByIdHandler.Handle")
	defer span.Finish()

	ctx = tracing.InjectTextMapCarrierToGrpcMetaData(ctx, span.Context())
	res, err := q.rsClient.GetFeedback(ctx, &readerService.GetFeedbackByIdReq{FeedbackID: query.FeedbackID.String()})
	if err != nil {
		return nil, err
	}

	return dto.FeedbackResponseFromGrpc(res.GetFeedback()), nil
}
