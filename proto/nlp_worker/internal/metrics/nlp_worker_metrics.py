from prometheus_client import Counter, Histogram, Gauge, Summary
import time


class NlpWorkerMetrics:
    """Metrics for NLP Worker Service"""
    
    def __init__(self):
        # Request counters
        self.create_feedback_analysis_grpc_requests = Counter(
            'nlp_worker_grpc_requests_total',
            'Total number of gRPC requests for feedback analysis'
        )
        
        self.success_grpc_requests = Counter(
            'nlp_worker_grpc_success_total',
            'Total number of successful gRPC requests'
        )
        
        self.failed_grpc_requests = Counter(
            'nlp_worker_grpc_failed_total',
            'Total number of failed gRPC requests'
        )
        
        # Processing metrics
        self.feedback_analysis_duration = Histogram(
            'nlp_worker_feedback_analysis_duration_seconds',
            'Time spent processing feedback analysis'
        )
        
        self.sentiment_analysis_duration = Histogram(
            'nlp_worker_sentiment_analysis_duration_seconds',
            'Time spent on sentiment analysis'
        )
        
        self.keyword_extraction_duration = Histogram(
            'nlp_worker_keyword_extraction_duration_seconds',
            'Time spent on keyword extraction'
        )
        
        # Quality metrics
        self.sentiment_distribution = Counter(
            'nlp_worker_sentiment_distribution_total',
            'Distribution of sentiment analysis results'
        )
        
        self.keyword_count = Histogram(
            'nlp_worker_keyword_count',
            'Number of keywords extracted per feedback'
        )
        
        # System metrics
        self.active_analysis_requests = Gauge(
            'nlp_worker_active_analysis_requests',
            'Number of feedback analysis requests currently being processed'
        )
        
        self.nlp_model_health = Gauge(
            'nlp_worker_nlp_model_health',
            'Health status of NLP models (1 = healthy, 0 = unhealthy)'
        )
        
        # Summary metrics
        self.feedback_analysis_summary = Summary(
            'nlp_worker_feedback_analysis_summary',
            'Summary of feedback analysis processing'
        )

        self.consumer_errors = Counter(
            'nlp_worker_consumer_errors', 'Number of Kafka consumer errors'
        )

        self.messages_received = Counter(
            'nlp_worker_messages_received', 'Number of messages received from Kafka'
        )

        self.send_errors = Counter(
            'nlp_worker_send_errors', 'Errors sending results to Kafka'
            )
        
        self.results_sent = Counter(
            'nlp_worker_results_sent', 'Number of results_sent to Kafka'
            )
        
        self.messages_processed = Counter(
            'nlp_worker_messages_processed', 'Number of messages processed from Kafka'
            )
    
    def record_feedback_analysis_duration(self, duration: float):
        """Record the duration of feedback analysis"""
        self.feedback_analysis_duration.observe(duration)
    
    def record_sentiment_analysis_duration(self, duration: float):
        """Record the duration of sentiment analysis"""
        self.sentiment_analysis_duration.observe(duration)
    
    def record_keyword_extraction_duration(self, duration: float):
        """Record the duration of keyword extraction"""
        self.keyword_extraction_duration.observe(duration)
    
    def record_sentiment_result(self, sentiment: str):
        """Record sentiment analysis result"""
        self.sentiment_distribution.inc()
    
    def record_keyword_count(self, keyword_count: int):
        """Record the number of keywords extracted"""
        self.keyword_count.observe(keyword_count)
    
    def set_active_requests(self, count: int):
        """Set the number of active analysis requests"""
        self.active_analysis_requests.set(count)
    
    def set_nlp_model_health(self, is_healthy: bool):
        """Set the health status of NLP models"""
        self.nlp_model_health.set(1 if is_healthy else 0)
    
    def record_feedback_analysis_summary(self, duration: float):
        """Record summary of feedback analysis"""
        self.feedback_analysis_summary.observe(duration)
    
    def get_metrics_summary(self) -> dict:
        """Get a summary of current metrics"""
        return {
            "total_requests": self.create_feedback_analysis_grpc_requests._value.get(),
            "successful_requests": self.success_grpc_requests._value.get(),
            "failed_requests": self.failed_grpc_requests._value.get(),
            "active_requests": self.active_analysis_requests._value.get(),
            "nlp_model_health": self.nlp_model_health._value.get()
        }
