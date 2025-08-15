import grpc
from concurrent import futures
import logging
import time

from grpc_reflection.v1alpha import reflection
from grpc_prometheus import PromServerInterceptor, start_http_server
from grpc_opentracing import open_tracing_server_interceptor

# Импортируй свои protobuf-сгенерированные классы
from proto.nlp_worker_reader import reader_pb2_grpc
from delivery.grpc.reader_grpc_service import ReaderGrpcService  # реализация сервиса


class GrpcConfig:
    def __init__(self, port="50051", development=True):
        self.port = port
        self.development = development


class Server:
    def __init__(self, config, logger, validator, processors, metrics):
        self.cfg = config
        self.log = logger
        self.v = validator
        self.ps = processors
        self.metrics = metrics

    def new_reader_grpc_server(self):
        interceptors = [
            PromServerInterceptor(),  # метрики Prometheus
            open_tracing_server_interceptor(),  # если используешь OpenTracing
            self.log.interceptor(),  # твой кастомный логгер, должен быть gRPC unary interceptor
        ]

        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            interceptors=interceptors,
            options=[
                ('grpc.keepalive_time_ms', 10 * 60 * 1000),
                ('grpc.keepalive_timeout_ms', 15 * 1000),
                ('grpc.keepalive_permit_without_calls', 1),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 5 * 60 * 1000),
                ('grpc.http2.min_ping_interval_without_data_ms', 5 * 60 * 1000),
            ]
        )

        # регистрация gRPC-сервиса
        reader_grpc_service = ReaderGrpcService(self.log, self.cfg, self.v, self.ps, self.metrics)
        reader_pb2_grpc.add_ReaderServiceServicer_to_server(reader_grpc_service, server)

        # Enable Prometheus metrics
        start_http_server(port=8000)  # порт для экспорта метрик
        PromServerInterceptor().register(server)

        # Enable reflection for development/debugging
        if self.cfg.development:
            SERVICE_NAMES = (
                reader_pb2_grpc.DESCRIPTOR.services_by_name['ReaderService'].full_name,
                reflection.SERVICE_NAME,
            )
            reflection.enable_server_reflection(SERVICE_NAMES, server)

        # Start server in background
        address = f"[::]:{self.cfg.port}"
        server.add_insecure_port(address)
        self.log.info(f"Reader gRPC server is listening on port: {self.cfg.port}")
        server.start()

        def stop_server():
            self.log.info("Stopping gRPC server...")
            server.stop(0)

        return stop_server, server
