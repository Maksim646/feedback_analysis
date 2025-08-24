import grpc
from concurrent import futures
import logging
import time
import sys

# Import our protobuf-generated classes
from proto.nlp_worker_reader import nlp_worker_reader_pb2_grpc
from internal.feedback_analysis.delivery.grpc.grpc_service import NlpWorkerGrpcService
from internal.feedback_analysis.service.feedback_analysis_service import FeedbackAnalysisService
from internal.feedback_analysis.repository.feedback_analysis_repository import FeedbackAnalysisRepository
from internal.metrics.nlp_worker_metrics import NlpWorkerMetrics
from internal.server.health_server import start_health_server
from config.config import Config


def serve(config: Config, metrics: NlpWorkerMetrics, logger: logging.Logger):
    """Start the gRPC server for NLP Worker Service"""
    try:
        logger.info("Starting NLP Worker gRPC server...")
    
        repository = FeedbackAnalysisRepository(config, logger)
        service = FeedbackAnalysisService(config, metrics, logger)
        
        # Start health check server
        health_thread = start_health_server(config.probes.port, metrics, logger)
        logger.info(f"Health check server started on port {config.probes.port}")
        
        # Create gRPC server
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            options=[
                ('grpc.keepalive_time_ms', 10 * 60 * 1000),
                ('grpc.keepalive_timeout_ms', 15 * 1000),
                ('grpc.keepalive_permit_without_calls', 1),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 5 * 60 * 1000),
                ('grpc.http2.min_ping_interval_without_data_ms', 5 * 60 * 1000),
            ]
        )
        
        # Register gRPC service
        nlp_worker_service = NlpWorkerGrpcService(logger, config, service, metrics)
        nlp_worker_reader_pb2_grpc.add_NlpWorkerServiceServicer_to_server(nlp_worker_service, server)
        
        # Start Prometheus metrics server (simplified)
        try:
            from prometheus_client import start_http_server
            start_http_server(port=config.probes.prometheusPort)
            logger.info(f"Prometheus metrics server started on port {config.probes.prometheusPort}")
        except Exception as e:
            logger.warning(f"Could not start Prometheus server: {e}")
        
        # Start server
        address = f"[::]:{config.grpc.port}"
        server.add_insecure_port(address)
        server.start()
        
        logger.info(f"NLP Worker gRPC server started successfully on port {config.grpc.port}")
        
        # Set model health to healthy
        metrics.set_nlp_model_health(True)
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal, stopping server...")
            server.stop(0)
            repository.close_connection()
            logger.info("Server stopped gracefully")
            
    except Exception as e:
        logger.error(f"Failed to start gRPC server: {e}")
        raise
