#!/usr/bin/env python3
"""
Kafka Consumer Service for NLP Worker
Consumes raw feedback messages and processes them through NLP analysis
"""

import json
import logging
import time
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError
from proto.nlp_worker_reader import nlp_worker_reader_pb2
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime

# from internal.feedback_analysis.repository.feedback_analysis_repository import FeedbackAnalysisRepository
from internal.feedback_analysis.service.feedback_analysis_service import FeedbackAnalysisService
from internal.feedback_analysis.models.feedback_analysis import FeedbackAnalysisRequest
from internal.metrics.nlp_worker_metrics import NlpWorkerMetrics


class KafkaConsumerService:
    """Kafka Consumer Service for processing feedback messages"""
    
    def __init__(self, config: Dict[str, Any], metrics: NlpWorkerMetrics):
        self.config = config
        self.metrics = metrics
        self.logger = logging.getLogger(__name__)
        
        # Initialize Kafka consumer
        self.consumer = KafkaConsumer(
            config.kafka.kafkaTopics.feedbackRaw.topicName,
            bootstrap_servers=config.kafka.brokers,
            group_id=config.kafka.groupID,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=protobuf_deserializer,
            # key_deserializer=lambda x: x.decode('utf-8') if x else None,
            # compression_type='snappy'
        )
        
        # Initialize Kafka producer for analyzed results
        self.producer = KafkaProducer(
            bootstrap_servers=config.kafka.brokers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None
        )
        
        # Initialize NLP service
        self.nlp_service = FeedbackAnalysisService(config, metrics, self.logger)
        
        # Thread pool for processing messages
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        self.logger.info("Kafka Consumer Service initialized")
    
    def start_consuming(self):
        """Start consuming messages from Kafka"""
        self.logger.info("Starting Kafka consumer...")

        # for msg in self.consumer:
        #     print(msg.value)
        
        try:
            for message in self.consumer:
                self.logger.info(f"Received message: {message.value}")
                
                # Process message asynchronously
                self.executor.submit(self._process_message, message)
                
                # Update metrics
                self.metrics.messages_received.inc()
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down consumer...")
        except Exception as e:
            self.logger.error(f"Error in consumer: {e}")
            self.metrics.consumer_errors.inc()
        finally:
            self._cleanup()
    
    def _process_message(self, message):
        try:
            feedback_data = message.value  # это CreateFeedbackAnalysisReq protobuf

            ts: Timestamp = feedback_data.created_at

            # Конвертируем в секунды
            unix_seconds = ts.seconds  # int

            # Если нужно в datetime
            created_dt = datetime.fromtimestamp(unix_seconds)

            # Если сообщение приходит как обычный dict (json) из Go
            # с полями feedback_id, feedback_source, feedback_text, feedback_timestamp
            feedback_id = getattr(feedback_data, 'feedback_id', None)
            feedback_source = getattr(feedback_data, 'feedback_source', 'unknown')
            text = getattr(feedback_data, 'feedback_text', getattr(feedback_data, 'text', ''))
            timestamp = getattr(feedback_data, 'feedback_timestamp', None)

            request = FeedbackAnalysisRequest(
                feedback_id=feedback_id,
                feedback_source=feedback_source,
                text=text,
                created_at=created_dt,
            )
            print(' Сообщение получили из кафки: ', request)

            result = self.nlp_service.analyze_feedback(feedback_id=feedback_id,
                feedback_source=feedback_source,
                text=text,
                created_at=created_dt,)
            self._send_analyzed_result(result)

            self.metrics.messages_processed.inc()
            if timestamp:
                self.metrics.processing_time.observe(time.time() - timestamp)

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            self.metrics.processing_errors.inc()

    
    def _send_analyzed_result(self, result: Dict[str, Any]):
        """Send analyzed result to output Kafka topic"""
        try:
            topic = self.config.kafka.kafkaTopics.feedbackAnalyzed.topicName
            
            print("Результат", result)
            # Convert result to dict for JSON serialization

            print(result)
            result_dict = {
                'feedback_id': result.feedback_id,
                'feedback_source': result.feedback_source,
                'text': result.text,
                'sentiment': result.sentiment,
                'keywords': result.keywords,
                'created_at': result.created_at.isoformat(),
            }
            
            print('Поехали в кафку отправлять в топик: ', topic, "данные: ", result_dict)
            # Send to Kafka
            future = self.producer.send(
                topic,
                key=str(result.feedback_id),
                value=result_dict
            )
            
            # Wait for send to complete
            record_metadata = future.get(timeout=10)
            
            self.logger.info(f"Sent analyzed result to {topic}: {record_metadata}")
            self.metrics.results_sent.inc()
            
        except Exception as e:
            self.logger.error(f"Error sending analyzed result: {e}")
            self.metrics.send_errors.inc()
    
    def _cleanup(self):
        """Clean up resources"""
        try:
            self.consumer.close()
            self.producer.close()
            self.executor.shutdown(wait=True)
            self.logger.info("Kafka Consumer Service cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def create_kafka_consumer_service(config: Dict[str, Any], metrics: NlpWorkerMetrics) -> KafkaConsumerService:
    """Factory function to create Kafka consumer service"""
    return KafkaConsumerService(config, metrics)

def protobuf_deserializer(msg_bytes):
    feedback = nlp_worker_reader_pb2.CreateFeedbackAnalysisReq()
    feedback.ParseFromString(msg_bytes)
    return feedback