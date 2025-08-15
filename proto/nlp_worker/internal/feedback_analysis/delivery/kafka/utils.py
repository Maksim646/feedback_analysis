import logging

class ReaderMessageProcessor:
    def __init__(self, metrics, logger):
        self.metrics = metrics
        self.log = logger  # должен поддерживать методы: kafka_log_committed_message(), warn_msg(), kafka_process_message()

    async def commit_message(self, consumer, message):
        self.metrics.success_kafka_messages.inc()
        self.log.kafka_log_committed_message(message.topic, message.partition, message.offset)

        try:
            await consumer.commit()
        except Exception as e:
            self.log.warn_msg("commit_message", e)

    def log_process_message(self, message, worker_id):
        value = message.value.decode('utf-8') if isinstance(message.value, bytes) else str(message.value)
        self.log.kafka_process_message(
            message.topic, message.partition, value, worker_id, message.offset, message.timestamp
        )

    async def commit_err_message(self, consumer, message):
        self.metrics.error_kafka_messages.inc()
        self.log.kafka_log_committed_message(message.topic, message.partition, message.offset)

        try:
            await consumer.commit()
        except Exception as e:
            self.log.warn_msg("commit_message", e)
