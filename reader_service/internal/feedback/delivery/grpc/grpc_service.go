package grpc

import (
	"context"

	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/pkg/tracing"

	// "github.com/Maksim646/feedback_analysis/pkg/utils"
	"github.com/Maksim646/feedback_analysis/reader_service/config"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/metrics"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/models"

	// "github.com/Maksim646/feedback_analysis/reader_service/internal/models"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/commands"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/queries"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/service"
	readerService "github.com/Maksim646/feedback_analysis/reader_service/proto/feedback_reader"
	"github.com/go-playground/validator"

	"time"

	uuid "github.com/satori/go.uuid"

	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type grpcService struct {
	log     logger.Logger
	cfg     *config.Config
	v       *validator.Validate
	ps      *service.FeedbackService
	metrics *metrics.ReaderServiceMetrics
}

func NewReaderGrpcService(log logger.Logger, cfg *config.Config, v *validator.Validate, ps *service.FeedbackService, metrics *metrics.ReaderServiceMetrics) *grpcService {
	return &grpcService{log: log, cfg: cfg, v: v, ps: ps, metrics: metrics}
}

func (s *grpcService) CreateFeedback(ctx context.Context, req *readerService.CreateFeedbackReq) (*readerService.CreateFeedbackRes, error) {
	// s.metrics.CreateFeedbackGrpcRequests.Inc()

	ctx, span := tracing.StartGrpcServerTracerSpan(ctx, "grpcService.CreateFeedback")

	defer span.Finish()

	command := commands.NewFeedbackAnalyzedCommand(req.GetFeedbackID(), req.GetText(), req.GetFeedbackSource(), req.GetKeywords(), req.GetSentiment(), time.Now())
	if err := s.v.StructCtx(ctx, command); err != nil {
		s.log.WarnMsg("validate", err)
		return nil, s.errResponse(codes.InvalidArgument, err)
	}

	if err := s.ps.Commands.CreateFeedbackAnalyzed.Handle(ctx, command); err != nil {
		s.log.WarnMsg("FeedbackAnalyzed.Handle", err)
		return nil, s.errResponse(codes.InvalidArgument, err)
	}

	s.metrics.SuccessGrpcRequests.Inc()
	return &readerService.CreateFeedbackRes{FeedbackID: req.GetFeedbackID()}, nil
}

// func (s *grpcService) UpdateProduct(ctx context.Context, req *readerService.UpdateProductReq) (*readerService.UpdateProductRes, error) {
// 	s.metrics.UpdateProductGrpcRequests.Inc()

// 	ctx, span := tracing.StartGrpcServerTracerSpan(ctx, "grpcService.UpdateProduct")
// 	defer span.Finish()

// 	command := commands.NewUpdateProductCommand(req.GetProductID(), req.GetName(), req.GetDescription(), req.GetPrice(), time.Now())
// 	if err := s.v.StructCtx(ctx, command); err != nil {
// 		s.log.WarnMsg("validate", err)
// 		return nil, s.errResponse(codes.InvalidArgument, err)
// 	}

// 	if err := s.ps.Commands.UpdateProduct.Handle(ctx, command); err != nil {
// 		s.log.WarnMsg("UpdateProduct.Handle", err)
// 		return nil, s.errResponse(codes.InvalidArgument, err)
// 	}

// 	s.metrics.SuccessGrpcRequests.Inc()
// 	return &readerService.UpdateProductRes{ProductID: req.GetProductID()}, nil
// }

func (s *grpcService) GetFeedback(ctx context.Context, req *readerService.GetFeedbackByIdReq) (*readerService.GetFeedbackByIdRes, error) {
	// s.metrics.GetProductByIdGrpcRequests.Inc()

	ctx, span := tracing.StartGrpcServerTracerSpan(ctx, "grpcService.GetFeedbackById")
	defer span.Finish()

	feedbackUUID, err := uuid.FromString(req.GetFeedbackID())
	if err != nil {
		s.log.WarnMsg("uuid.FromString", err)
		return nil, s.errResponse(codes.InvalidArgument, err)
	}

	query := queries.NewGetFeedbackByIdQuery(feedbackUUID)
	if err := s.v.StructCtx(ctx, query); err != nil {
		s.log.WarnMsg("validate", err)
		return nil, s.errResponse(codes.InvalidArgument, err)
	}

	feedback, err := s.ps.Queries.GetFeedbackById.Handle(ctx, query)
	if err != nil {
		s.log.WarnMsg("GetFeedbackById.Handle", err)
		return nil, s.errResponse(codes.Internal, err)
	}

	s.metrics.SuccessGrpcRequests.Inc()
	return &readerService.GetFeedbackByIdRes{Feedback: models.FeedbackToGrpcMessage(feedback)}, nil
}

// func (s *grpcService) SearchProduct(ctx context.Context, req *readerService.SearchReq) (*readerService.SearchRes, error) {
// 	s.metrics.SearchProductGrpcRequests.Inc()

// 	ctx, span := tracing.StartGrpcServerTracerSpan(ctx, "grpcService.SearchProduct")
// 	defer span.Finish()

// 	pq := utils.NewPaginationQuery(int(req.GetSize()), int(req.GetPage()))

// 	query := queries.NewSearchProductQuery(req.GetSearch(), pq)
// 	productsList, err := s.ps.Queries.SearchProduct.Handle(ctx, query)
// 	if err != nil {
// 		s.log.WarnMsg("SearchProduct.Handle", err)
// 		return nil, s.errResponse(codes.Internal, err)
// 	}

// 	s.metrics.SuccessGrpcRequests.Inc()
// 	return models.ProductListToGrpc(productsList), nil
// }

// func (s *grpcService) DeleteProductByID(ctx context.Context, req *readerService.DeleteProductByIdReq) (*readerService.DeleteProductByIdRes, error) {
// 	s.metrics.DeleteProductGrpcRequests.Inc()

// 	ctx, span := tracing.StartGrpcServerTracerSpan(ctx, "grpcService.DeleteProductByID")
// 	defer span.Finish()

// 	productUUID, err := uuid.FromString(req.GetProductID())
// 	if err != nil {
// 		s.log.WarnMsg("uuid.FromString", err)
// 		return nil, s.errResponse(codes.InvalidArgument, err)
// 	}

// 	if err := s.ps.Commands.DeleteProduct.Handle(ctx, commands.NewDeleteProductCommand(productUUID)); err != nil {
// 		s.log.WarnMsg("DeleteProduct.Handle", err)
// 		return nil, s.errResponse(codes.Internal, err)
// 	}

// 	s.metrics.SuccessGrpcRequests.Inc()
// 	return &readerService.DeleteProductByIdRes{}, nil
// }

func (s *grpcService) errResponse(c codes.Code, err error) error {
	s.metrics.ErrorGrpcRequests.Inc()
	return status.Error(c, err.Error())
}
