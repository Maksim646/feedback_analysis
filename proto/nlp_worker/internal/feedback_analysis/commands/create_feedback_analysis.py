from typing import Protocol
from datetime import datetime
from abc import ABC, abstractmethod

from opentracing_instrumentation.request_context import span_in_context
from config.config import Config
from internal.models.feedback_analysis import FeedbackAnalysis
from feedback_analysis.repository.repository import Repository
from feedback_analysis.repository.cache_repository import CacheRepository
from feedback_analysis.commands.commands import CreateFeedbackAnalysisCommand


class CreateFeedbackAnalysisCmdHandler(Protocol):
    def handle(self, ctx, command: CreateFeedbackAnalysisCommand) -> None:
        ...


class CreateFeedbackAnalysisHandler:
    def __init__(
        self,
        logger,
        cfg: Config,
        mongo_repo: Repository,
        redis_repo: CacheRepository
    ):
        self.log = logger
        self.cfg = cfg
        self.mongo_repo = mongo_repo
        self.redis_repo = redis_repo

    def handle(self, ctx, command: CreateFeedbackAnalysisCommand) -> None:
        with span_in_context("CreateFeedbackAnalysisHandler.handle"):
            feedback_analysis = FeedbackAnalysis(
                feedback_id=command.feedback_id,
                source=command.source,
                text=command.text,
                keywords=command.keywords,
                sentiment=command.sentiment,
                created_at=command.created_at
            )

            created = self.mongo_repo.create_feedback_analysis(ctx, feedback_analysis)
            self.redis_repo.put_feedback_analysis(ctx, created.feedback_id, created)
