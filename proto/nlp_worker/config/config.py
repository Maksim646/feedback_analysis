import yaml
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GrpcConfig:
    port: int
    development: bool


@dataclass
class ProbesConfig:
    readinessPath: str
    livenessPath: str
    port: int
    pprof: int
    prometheusPath: str
    prometheusPort: int
    checkIntervalSeconds: int


@dataclass
class LoggerConfig:
    level: str
    devMode: bool
    encoder: str


@dataclass
class NlpConfig:
    model_name: str
    sentiment_threshold: float
    max_keywords: int
    language: str


@dataclass
class KafkaTopicConfig:
    topicName: str
    partitions: int
    replicationFactor: int


@dataclass
class KafkaTopicsConfig:
    feedbackRaw: KafkaTopicConfig
    feedbackCreate: KafkaTopicConfig
    feedbackAnalyzed: KafkaTopicConfig


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
class MongoCollectionsConfig:
    feedback_analysis: str
    keywords: str
    sentiment_history: str


@dataclass
class MongoConfig:
    uri: str
    user: str
    password: str
    db: str
    collections: MongoCollectionsConfig


@dataclass
class JaegerConfig:
    enable: bool
    serviceName: str
    hostPort: str
    logSpans: bool


@dataclass
class Config:
    serviceName: str
    grpc: GrpcConfig
    probes: ProbesConfig
    logger: LoggerConfig
    nlp: NlpConfig
    kafka: KafkaConfig
    redis: RedisConfig
    mongo: MongoConfig
    jaeger: JaegerConfig


def load_config(path="config/config.yaml") -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Вспомогательная функция для рекурсивного создания dataclass из dict
    def from_dict(cls, data_dict):
        fieldtypes = {f.name: f.type for f in cls.__dataclass_fields__.values()}
        return cls(**{f: from_dict(fieldtypes[f], data_dict[f]) if hasattr(fieldtypes[f], "__dataclass_fields__") else data_dict[f] for f in data_dict})

    return from_dict(Config, data)
