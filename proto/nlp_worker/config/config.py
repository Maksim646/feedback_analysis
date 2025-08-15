import yaml
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GrpcConfig:
    port: str
    development: bool


@dataclass
class ProbesConfig:
    readinessPath: str
    livenessPath: str
    port: str
    pprof: str
    prometheusPath: str
    prometheusPort: str
    checkIntervalSeconds: int


@dataclass
class LoggerConfig:
    level: str
    devMode: bool
    encoder: str


@dataclass
class PostgresConfig:
    host: str
    port: int
    user: str
    password: str
    dbName: str
    sslMode: bool


@dataclass
class KafkaTopicConfig:
    topicName: str
    partitions: int
    replicationFactor: int


@dataclass
class KafkaTopicsConfig:
    productCreate: KafkaTopicConfig
    productUpdate: KafkaTopicConfig
    productCreated: KafkaTopicConfig
    productUpdated: KafkaTopicConfig
    productDeleted: KafkaTopicConfig


@dataclass
class KafkaConfig:
    brokers: List[str]
    groupID: str
    initTopics: bool
    kafkaTopics: KafkaTopicsConfig


@dataclass
class RedisConfig:
    addr: str
    password: str
    db: int
    poolSize: int


@dataclass
class MongoConfig:
    uri: str
    user: str
    password: str
    db: str


@dataclass
class MongoCollectionsConfig:
    products: str


@dataclass
class JaegerConfig:
    enable: bool
    serviceName: str
    hostPort: str
    logSpans: bool


@dataclass
class ServiceSettingsConfig:
    redisProductPrefixKey: str


@dataclass
class Config:
    serviceName: str
    grpc: GrpcConfig
    probes: ProbesConfig
    logger: LoggerConfig
    postgres: PostgresConfig
    kafka: KafkaConfig
    redis: RedisConfig
    mongo: MongoConfig
    mongoCollections: MongoCollectionsConfig
    serviceSettings: ServiceSettingsConfig
    jaeger: JaegerConfig


def load_config(path="config/config.yaml") -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Вспомогательная функция для рекурсивного создания dataclass из dict
    def from_dict(cls, data_dict):
        fieldtypes = {f.name: f.type for f in cls.__dataclass_fields__.values()}
        return cls(**{f: from_dict(fieldtypes[f], data_dict[f]) if hasattr(fieldtypes[f], "__dataclass_fields__") else data_dict[f] for f in data_dict})

    return from_dict(Config, data)
