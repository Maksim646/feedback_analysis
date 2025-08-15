import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from prometheus_client import start_http_server, Summary
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from fastapi.responses import Response
from redis.asyncio import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from confluent_kafka.admin import AdminClient
import signal
import os

logger = logging.getLogger("nlp_worker")
logger.setLevel(logging.INFO)

class Server:
    def __init__(self, cfg):
        self.cfg = cfg
        self.redis_client: Redis | None = None
        self.mongo_client: AsyncIOMotorClient | None = None
        self.kafka_admin: AdminClient | None = None

    async def connect_kafka(self):
        self.kafka_admin = AdminClient({"bootstrap.servers": self.cfg["kafka"]["brokers"]})
        try:
            brokers = self.kafka_admin.list_topics(timeout=5).brokers
            logger.info(f"Kafka connected to brokers: {list(brokers.keys())}")
        except Exception as e:
            raise RuntimeError(f"Kafka connection error: {e}")

    async def connect_mongo(self):
        self.mongo_client = AsyncIOMotorClient(self.cfg["mongo"]["uri"])
        await self.mongo_client.admin.command("ping")
        logger.info("MongoDB connected")

    async def connect_redis(self):
        self.redis_client = Redis.from_url(self.cfg["redis"]["url"])
        await self.redis_client.ping()
        logger.info("Redis connected")

    async def health_check(self):
        async def readiness():
            try:
                await self.redis_client.ping()
                await self.mongo_client.admin.command("ping")
                self.kafka_admin.list_topics(timeout=2)
                return True
            except Exception as e:
                logger.warning(f"Readiness check failed: {e}")
                return False

        app = FastAPI()

        @app.get("/live")
        async def live():
            return {"status": "alive"}

        @app.get("/ready")
        async def ready():
            if await readiness():
                return {"status": "ready"}
            return Response(status_code=503)

        port = int(self.cfg["probes"]["port"])
        logger.info(f"Kubernetes probes listening on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)

    async def run_metrics_server(self):
        prometheus_port = int(self.cfg["probes"]["prometheus_port"])
        logger.info(f"Prometheus metrics server running on port {prometheus_port}")
        start_http_server(prometheus_port)

    async def run(self):
        await self.connect_mongo()
        await self.connect_redis()
        await self.connect_kafka()

        # Start health checks and metrics server in background
        asyncio.create_task(self.health_check())
        asyncio.create_task(self.run_metrics_server())

        # Graceful shutdown
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

    async def shutdown(self):
        logger.info("Shutting down...")
        if self.redis_client:
            await self.redis_client.close()
        if self.mongo_client:
            self.mongo_client.close()

