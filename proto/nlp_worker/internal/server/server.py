import asyncio
import signal
import logging

from concurrent import futures
from contextlib import suppress

from redis import Redis
from pymongo import MongoClient
from kafka import KafkaConsumer
from prometheus_client import start_http_server
from opentracing import global_tracer, set_global_tracer

from config import Config
from interceptors import InterceptorManager
from internal.metrics import ReaderServiceMetrics
from internal.product.service import ProductService
from internal.product.delivery.kafka.reader_kafka import ReaderMessageProcessor
from internal.product.repository.mongo_repository import MongoRepository
from internal.product.repository.redis_repository import RedisRepository
from pkg.kafka_client import ConsumerGroup
from pkg.tracing import init_jaeger_tracer
from grpc_server import Server as GrpcServer


class Server:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.log = logging.getLogger("reader_server")
        self.v = None  # можешь подключить `pydantic` или `cerberus` для валидации
        self.im = InterceptorManager(self.log)
        self.mongo_client = None
        self.redis_client = None
        self.kafka_conn = None
        self.ps = None
        self.metrics = ReaderServiceMetrics(cfg)

    async def run(self):
        loop = asyncio.get_event_loop()

        # Graceful shutdown
        stop_event = asyncio.Event()

        def _shutdown():
            self.log.info("Shutting down service...")
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, _shutdown)

        # MongoDB
        self.mongo_client = MongoClient(self.cfg.mongo.uri)
        self.log.info("MongoDB connected")

        # Redis
        self.redis_client = Redis.from_url(self.cfg.redis.url)
        self.log.info("Redis connected")

        # Repositories
        mongo_repo = MongoRepository(self.log, self.cfg, self.mongo_client)
        redis_repo = RedisRepository(self.log, self.cfg, self.redis_client)

        # Service
        self.ps = ProductService(self.log, self.cfg, mongo_repo, redis_repo)

        # Kafka consumer
        reader_processor = ReaderMessageProcessor(
            self.log, self.cfg, self.v, self.ps, self.metrics
        )

        self.log.info("Starting Kafka consumer group")
        consumer_group = ConsumerGroup(self.cfg.kafka.brokers, self.cfg.kafka.group_id, self.log)
        kafka_task = asyncio.create_task(
            consumer_group.consume_topics(
                self.get_consumer_group_topics(),
                self.cfg.kafka.pool_size,
                reader_processor.process_messages
            )
        )

        # Jaeger tracing
        if self.cfg.jaeger.enable:
            tracer, closer = init_jaeger_tracer(self.cfg.jaeger)
            set_global_tracer(tracer)
            self.log.info("Jaeger tracer initialized")

        # Start Prometheus metrics
        start_http_server(self.cfg.metrics.port)
        self.log.info(f"Metrics server started on port {self.cfg.metrics.port}")

        # gRPC server
        grpc_server = GrpcServer(self.cfg, self.log, self.v, self.ps, self.metrics)
        stop_grpc, grpc_srv = grpc_server.new_reader_grpc_server()

        await stop_event.wait()

        # Cleanup
        stop_grpc()
        kafka_task.cancel()
        with suppress(asyncio.CancelledError):
            await kafka_task

        self.mongo_client.close()
        self.redis_client.close()
        self.log.info("Server shutdown complete.")

    def get_consumer_group_topics(self):
        return self.cfg.kafka.topics
