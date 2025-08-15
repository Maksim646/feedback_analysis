import logging
import json
from retrying import retry
from google.protobuf.message import DecodeError
from google.protobuf.timestamp_pb2 import Timestamp
from proto.kafka.feedback_analysis_created_pb2 import FeedbackAnalysisCreated
from internal.product.commands import CreateFeedbackAnalysisCommand
from internal.tracing import start_kafka_consumer_tracer_span


RETRY_ATTEMPTS = 3
RETRY_DELAY_MS = 300


class ReaderMessageProcessor:
    def process_feedback_analysis_created(self, ctx, consumer, message):
        self.metrics.create_feedback_analysis_kafka_messages.inc()

        with start_kafka_consumer_tracer_span(ctx, message.headers, "ReaderMessageProcessor.process_feedback_analysis_created") as span:
            try:
                msg = FeedbackAnalysisCreated()
                msg.ParseFromString(message.value)
            except DecodeError as e:
                self.log.warning(f"proto.Unmarshal error: {e}")
                self.commit_err_message(ctx, consumer, message)
                return

            fa = msg.feedback_analysis

            try:
                command = CreateFeedbackAnalysisCommand(
                    feedback_id=fa.feedback_id,
                    source=fa.source,
                    text=fa.text,
                    keywords=list(fa.keywords),
                    sentiment=fa.sentiment,
                    created_at=fa.created_at.ToDatetime() if isinstance(fa.created_at, Timestamp) else datetime.utcnow()
                )
                self.validator.validate(command)  # Зависит от выбранной валидации
            except Exception as e:
                self.log.warning(f"Validation error: {e}")
                self.commit_err_message(ctx, consumer, message)
                return

            try:
                self._retry_handle(ctx, command)
            except Exception as e:
                self.log.warning(f"CreateFeedbackAnalysis.Handle failed: {e}")
                self.metrics.error_kafka_messages.inc()
                return

            self.commit_message(ctx, consumer, message)

    @retry(stop_max_attempt_number=RETRY_ATTEMPTS, wait_fixed=RETRY_DELAY_MS)
    def _retry_handle(self, ctx, command):
        self.service.commands.create_feedback_analysis.handle(ctx, command)
