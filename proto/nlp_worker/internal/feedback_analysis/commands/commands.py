from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class CreateFeedbackAnalysisCommand:
    feedback_id: str
    source: str
    text: str
    keywords: str  # Обрати внимание: keywords здесь строка, а не список
    sentiment: List[str]
    created_at: datetime

    @staticmethod
    def new(feedback_id: str, source: str, text: str, keywords: str, sentiment: List[str], created_at: datetime) -> 'CreateFeedbackAnalysisCommand':
        return CreateFeedbackAnalysisCommand(
            feedback_id=feedback_id,
            source=source,
            text=text,
            keywords=keywords,
            sentiment=sentiment,
            created_at=created_at
        )


class FeedbackAnalysisCommands:
    def __init__(self, create_feedback_analysis):
        self.create_feedback_analysis = create_feedback_analysis
