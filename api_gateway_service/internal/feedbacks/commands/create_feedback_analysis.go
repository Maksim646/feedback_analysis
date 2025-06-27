package commands

import (
	"context"
	"time"

	"github.com/Maksim646/feedback_analysis/api_gateway_service/config"
	kafkaClient "github.com/Maksim646/feedback_analysis/pkg/kafka"
	"github.com/Maksim646/feedback_analysis/pkg/logger"
	"github.com/Maksim646/feedback_analysis/pkg/tracing"
	kafkaMessages "github.com/Maksim646/feedback_analysis/proto/kafka"
	"github.com/opentracing/opentracing-go"
	"github.com/segmentio/kafka-go"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type CreateFeedbackAnalysisCmdHandler interface {
	Handle(ctx context.Context, command *CreateFeedbackAnalysisCommand) error
}

type createFeedbackAnalysisHandler struct {
	log           logger.Logger
	cfg           *config.Config
	kafkaProducer kafkaClient.Producer
}

func NewCreateFeedbackAnalysisHandler(log logger.Logger, cfg *config.Config, kafkaProducer kafkaClient.Producer) *createFeedbackAnalysisHandler {
	return &createFeedbackAnalysisHandler{log: log, cfg: cfg, kafkaProducer: kafkaProducer}
}

func (c *createFeedbackAnalysisHandler) Handle(ctx context.Context, command *CreateFeedbackAnalysisCommand) error {
	span, ctx := opentracing.StartSpanFromContext(ctx, "createFeedbackAnalysisHandler.Handle")
	defer span.Finish()

	createDto := &kafkaMessages.FeedbackAnalysisCreate{
		FeedbackID:        command.CreateDto.FeedbackID.String(),
		FeedbackSource:    command.CreateDto.FeedbackSource,
		Text:              command.CreateDto.Text,
		FeedbackTimestamp: timestamppb.New(time.Unix(command.CreateDto.FeedbackTimestamp, 0)),
	}

	dtoBytes, err := proto.Marshal(createDto)
	if err != nil {
		return err
	}

	return c.kafkaProducer.PublishMessage(ctx, kafka.Message{
		Topic:   c.cfg.KafkaTopics.RawFeedback.TopicName,
		Value:   dtoBytes,
		Time:    time.Now().UTC(),
		Headers: tracing.GetKafkaTracingHeadersFromSpanCtx(span.Context()),
	})
}
