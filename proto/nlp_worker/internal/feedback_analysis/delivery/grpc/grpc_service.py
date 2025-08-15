import grpc
from datetime import datetime

from grpc_interceptor.exceptions import GrpcException
from grpc_interceptor import ServerInterceptor

from proto import product_reader_pb2, product_reader_pb2_grpc
from config.config import Config
from internal.product.service import ProductService
from internal.product.commands.commands import CreateFeedbackAnalysisCommand
from internal.metrics.reader_service_metrics import ReaderServiceMetrics


class ReaderGRPCService(product_reader_pb2_grpc.NlpWorkerServiceServicer):
    def __init__(self, logger, cfg: Config, validator, service: ProductService, metrics: ReaderServiceMetrics):
        self.log = logger
        self.cfg = cfg
        self.validator = validator
        self.service = service
        self.metrics = metrics

    def CreateFeedbackAnalysis(self, request, context):
        self.metrics.create_feedback_analysis_grpc_requests.inc()

        # Трейсинг можно встроить здесь, если ты используешь opentelemetry или jaeger_client
        self.log.info("CreateFeedbackAnalysis gRPC called")

        command = CreateFeedbackAnalysisCommand(
            feedback_id=request.product_id,
            source=request.name,
            text=request.description,
            keywords=request.price,  # скорее всего, нужно заменить, т.к. тип некорректен
            sentiment=[],            # заполняется после анализа
            created_at=datetime.utcnow()
        )

        try:
            self.validator.validate(command)  # предположим, что ты используешь `pydantic` или `cerberus`
        except Exception as e:
            self.log.warn(f"Validation error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))

        try:
            self.service.commands.create_product.handle(context, command)
        except Exception as e:
            self.log.warn(f"Handler error: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))

        self.metrics.success_grpc_requests.inc()

        return product_reader_pb2.CreateProductRes(product_id=request.product_id)
