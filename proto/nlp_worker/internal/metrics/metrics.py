from prometheus_client import Counter, start_http_server
import logging

class ReaderServiceMetrics:
    def __init__(self, service_name: str, logger: logging.Logger):
        self.logger = logger

        self.success_grpc_requests = Counter(
            f"{service_name}_success_grpc_requests_total",
            "The total number of successful gRPC requests"
        )
        self.error_grpc_requests = Counter(
            f"{service_name}_error_grpc_requests_total",
            "The total number of errored gRPC requests"
        )
        self.create_feedback_analysis_grpc_requests = Counter(
            f"{service_name}_create_feedback_analysis_grpc_requests_total",
            "The total number of create feedback analysis gRPC requests"
        )
        self.create_feedback_analysis_kafka_messages = Counter(
            f"{service_name}_create_feedback_analysis_kafka_messages_total",
            "The total number of create feedback analysis kafka messages"
        )
        self.success_kafka_messages = Counter(
            f"{service_name}_success_kafka_processed_messages_total",
            "The total number of successful kafka processed messages"
        )
        self.error_kafka_messages = Counter(
            f"{service_name}_error_kafka_processed_messages_total",
            "The total number of error kafka processed messages"
        )


    def start_metrics_server(self, port=8003):
        self.logger.info(f"Starting Prometheus metrics HTTP server on port {port}")
        start_http_server(port)
