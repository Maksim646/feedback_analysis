from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FeedbackAnalysisResult:
    """Model representing the result of feedback analysis"""
    feedback_id: str
    feedback_source: str
    text: str
    created_at: datetime
    keywords: str
    sentiment: str
    analyzed_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            "feedback_id": self.feedback_id,
            "feedback_source": self.feedback_source,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
            "keywords": self.keywords,
            "sentiment": self.sentiment,
            "analyzed_at": self.analyzed_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FeedbackAnalysisResult':
        """Create from dictionary"""
        return cls(
            feedback_id=data["feedback_id"],
            feedback_source=data["feedback_source"],
            text=data["text"],
            created_at=datetime.fromisoformat(data["created_at"]),
            keywords=data["keywords"],
            sentiment=data["sentiment"],
            analyzed_at=datetime.fromisoformat(data["analyzed_at"])
        )


@dataclass
class FeedbackAnalysisRequest:
    """Model representing a feedback analysis request"""
    feedback_id: str
    feedback_source: str
    text: str
    created_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "feedback_id": self.feedback_id,
            "feedback_source": self.feedback_source,
            "text": self.text,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class SentimentStatistics:
    """Model representing sentiment statistics"""
    total_feedback: int
    positive_count: int
    negative_count: int
    neutral_count: int
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float
    feedback_source: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "total_feedback": self.total_feedback,
            "positive_count": self.positive_count,
            "negative_count": self.negative_count,
            "neutral_count": self.neutral_count,
            "positive_percentage": round(self.positive_percentage, 2),
            "negative_percentage": round(self.negative_percentage, 2),
            "neutral_percentage": round(self.neutral_percentage, 2),
            "feedback_source": self.feedback_source
        }
