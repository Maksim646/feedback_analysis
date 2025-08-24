#!/usr/bin/env python3
"""
NLP Worker Service Main Entry Point
Handles both gRPC server and Kafka consumer
"""

import logging
import argparse
import sys
import os
import signal
import threading
from concurrent.futures import ThreadPoolExecutor

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import load_config
from internal.server.grpc_server import serve
from internal.server.health_server import start_health_server
from internal.kafka.consumer import create_kafka_consumer_service
from internal.metrics.nlp_worker_metrics import NlpWorkerMetrics


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def start_kafka_consumer(config, metrics, logger):
    """Start Kafka consumer service"""
    try:
        kafka_service = create_kafka_consumer_service(config, metrics)
        logger.info("Starting Kafka consumer service...")
        kafka_service.start_consuming()
    except Exception as e:
        logger.error(f"Failed to start Kafka consumer: {e}")
        raise


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="NLP Worker Service")
    parser.add_argument('--config', default='config/config.yaml', help='Path to config file')
    parser.add_argument('--kafka-only', action='store_true', help='Run only Kafka consumer (no gRPC)')
    parser.add_argument('--grpc-only', action='store_true', help='Run only gRPC server (no Kafka)')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting NLP Worker Service...")
    
    try:
        # Load configuration
        config = load_config(args.config)
        logger.info("Configuration loaded successfully")
        
        # Initialize metrics
        metrics = NlpWorkerMetrics()
        logger.info("Metrics initialized")
        
        # Start health server
        health_thread = threading.Thread(
            target=start_health_server,
            args=(config.probes.port, logger),
            daemon=True
        )
        health_thread.start()
        logger.info(f"Health server started on port {config.probes.port}")
        
        # Create thread pool for services
        executor = ThreadPoolExecutor(max_workers=2)
        
        if not args.kafka_only:
            # Start gRPC server
            grpc_future = executor.submit(serve, config, metrics, logger)
            logger.info("gRPC server started")
        
        if not args.grpc_only:
            # Start Kafka consumer
            kafka_future = executor.submit(start_kafka_consumer, config, metrics, logger)
            logger.info("Kafka consumer started")
        
        # Wait for services to complete
        if not args.kafka_only:
            grpc_future.result()
        if not args.grpc_only:
            kafka_future.result()

        if 'grpc_future' in locals():
            grpc_future.result()
        if 'kafka_future' in locals():
            kafka_future.result()

            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        sys.exit(1)
    finally:
        executor.shutdown(wait=True)
        logger.info("Service shutdown complete")


if __name__ == "__main__":
    main()
