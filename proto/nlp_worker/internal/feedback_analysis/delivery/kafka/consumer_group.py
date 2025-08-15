import threading
import logging
from kafka import KafkaConsumer
from contextlib import suppress
from internal.metrics.reader_service_metrics import ReaderServiceMetrics
from internal.product.service import FeedbackAnalysisService
from config.config import Config
from internal.kafka.message_handlers import handle_feedback_analysis_created  # предполагаемая функция
import json


POOL_SIZE = 30


class ReaderMessageProcessor:
    def __init__(self, logger: logging.Logger, cfg: Config, validator, service: FeedbackAnalysisService, metrics: ReaderServiceMetrics):
        self.log = logger
        self.cfg = cfg
        self.validator = validator
        self.service = service
        self.metrics = metrics

    def process_messages(self, ctx, consumer: KafkaConsumer, worker_id: int):
        """
        Метод, который запускается в потоке/воркере
        """
        while not ctx.is_set():  # ctx — threading.Event, аналог context.Context.Done()
            try:
                message = next(consumer)
            except Exception as e:
                self.log.warning(f"Worker {worker_id}: error fetching message: {e}")
                continue

            self.log.info(f"Worker {worker_id}: Received message: topic={message.topic}, partition={message.partition}, offset={message.offset}")

            if message.topic == self.cfg.kafka_topics.feedback_analysis_created.topic_name:
                self.process_feedback_analysis_created(ctx, consumer, message)

    def process_feedback_analysis_created(self, ctx, consumer: KafkaConsumer, message):
        """
        Примерная обработка сообщения по топику `feedback_analysis_created`
        """
        try:
            data = json.loads(message.value.decode("utf-8"))
            handle_feedback_analysis_created(data, self.service, self.validator, self.log)
            consumer.commit()  # вручную фиксируем offset (если enable_auto_commit=False)
        except Exception as e:
            self.log.error(f"Failed to process feedback_analysis_created message: {e}")
