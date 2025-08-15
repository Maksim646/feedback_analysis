from dataclasses import dataclass
from datetime import datetime
from typing import List
from google.protobuf.timestamp_pb2 import Timestamp
import nlp_worker_pb2  # Импорт сгенерированного protobuf-модуля


@dataclass
class FeedbackAnalysis:
    feedback_analysis_id: str
    source: str
    text: str
    keywords: List[str]
    sentiment: str
    created_at: datetime

    def to_grpc_message(self) -> nlp_worker_pb2.CreateFeedbackAnalysisRes:
        created_at_ts = Timestamp()
        created_at_ts.FromDatetime(self.created_at)

        return nlp_worker_pb2.CreateFeedbackAnalysisRes(
            FeedbackID=self.feedback_analysis_id,
            FeedbackSource=self.source,
            Text=self.text,
            Keywords=self.keywords,  # protobuf repeated string — просто передаем список
            Sentiment=self.sentiment,
            CreatedAt=created_at_ts,
        )
