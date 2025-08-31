package kafka

import (
	"context"
	"time"

	"github.com/Maksim646/feedback_analysis/pkg/tracing"
	kafkaMessages "github.com/Maksim646/feedback_analysis/proto/kafka"
	"github.com/Maksim646/feedback_analysis/reader_service/internal/feedback/commands"
	"github.com/avast/retry-go"
	"github.com/segmentio/kafka-go"
	"google.golang.org/protobuf/proto"
)

const (
	retryAttempts = 3
	retryDelay    = 300 * time.Millisecond
)

var (
	retryOptions = []retry.Option{retry.Attempts(retryAttempts), retry.Delay(retryDelay), retry.DelayType(retry.BackOffDelay)}
)

func (s *readerMessageProcessor) processFeedbackCreated(ctx context.Context, r *kafka.Reader, m kafka.Message) {
	s.metrics.CreateProductKafkaMessages.Inc()

	ctx, span := tracing.StartKafkaConsumerTracerSpan(ctx, m.Headers, "readerMessageProcessor.processFeedbackCreated")
	defer span.Finish()

	msg := &kafkaMessages.FeedbackCreated{}
	if err := proto.Unmarshal(m.Value, msg); err != nil {
		s.log.WarnMsg("proto.Unmarshal", err)
		s.commitErrMessage(ctx, r, m)
		return
	}

	p := msg.GetFeedback()
	command := commands.NewFeedbackAnalyzedCommand(p.GetFeedbackID(), p.GetText(), p.GetFeedbackSource(), p.GetKeywords(), p.GetSentiment(), p.GetFeedbackTimestamp().AsTime())
	if err := s.v.StructCtx(ctx, command); err != nil {
		s.log.WarnMsg("validate", err)
		s.commitErrMessage(ctx, r, m)
		return
	}

	if err := retry.Do(func() error {
		return s.ps.Commands.CreateFeedbackAnalyzed.Handle(ctx, command)
	}, append(retryOptions, retry.Context(ctx))...); err != nil {
		s.log.WarnMsg("CreateFeedback.Handle", err)
		s.metrics.ErrorKafkaMessages.Inc()
		return
	}

	s.commitMessage(ctx, r, m)
}
