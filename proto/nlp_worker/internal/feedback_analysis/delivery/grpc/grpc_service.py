import grpc
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

from proto.nlp_worker_reader import nlp_worker_reader_pb2, nlp_worker_reader_pb2_grpc
from config.config import Config
from internal.feedback_analysis.service.feedback_analysis_service import FeedbackAnalysisService
from internal.metrics.nlp_worker_metrics import NlpWorkerMetrics


class NlpWorkerGrpcService(nlp_worker_reader_pb2_grpc.NlpWorkerServiceServicer):
    def __init__(self, logger, cfg: Config, service: FeedbackAnalysisService, metrics: NlpWorkerMetrics):
        self.log = logger
        self.cfg = cfg
        self.service = service
        self.metrics = metrics

    def CreateFeedbackAnalysis(self, request, context):
        """Process feedback text and return sentiment analysis and keywords"""
        self.metrics.create_feedback_analysis_grpc_requests.inc()
        
        try:
            self.log.info(f"Processing feedback analysis for ID: {request.feedback_id}")
            
            # Convert protobuf timestamp to datetime
            created_at = datetime.fromtimestamp(request.created_at.seconds + request.created_at.nanos / 1e9)
            
            # Analyze the feedback text
            analysis_result = self.service.analyze_feedback(
                feedback_id=request.feedback_id,
                feedback_source=request.feedback_source,
                text=request.text,
                created_at=created_at
            )
            
            # Create response
            response = nlp_worker_reader_pb2.CreateFeedbackAnalysisRes(
                feedback_id=analysis_result.feedback_id,
                feedback_source=analysis_result.feedback_source,
                text=analysis_result.text,
                created_at=request.created_at,  # Keep original timestamp
                keywords=analysis_result.keywords,
                sentiment=analysis_result.sentiment
            )
            
            self.metrics.success_grpc_requests.inc()
            self.log.info(f"Successfully analyzed feedback {request.feedback_id}")
            
            return response
            
        except Exception as e:
            self.log.error(f"Error processing feedback analysis: {str(e)}")
            self.metrics.failed_grpc_requests.inc()
            context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
