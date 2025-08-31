import logging
from typing import List, Optional
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from internal.feedback_analysis.models.feedback_analysis import FeedbackAnalysisResult
from config.config import Config


class FeedbackAnalysisRepository:
    """Repository for storing and retrieving feedback analysis results"""
    
    def __init__(self, config: Config, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.collection: Optional[Collection] = None
        
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        try:
            # Create MongoDB client
            if self.config.mongo.user and self.config.mongo.password:
                connection_string = f"mongodb://{self.config.mongo.user}:{self.config.mongo.password}@{self.config.mongo.uri.replace('mongodb://', '')}"
            else:
                connection_string = self.config.mongo.uri
            
            self.client = MongoClient(connection_string)
            self.db = self.client[self.config.mongo.db]
            self.collection = self.db[self.config.mongo.collections.feedback_analysis]
            
            # Create indexes for better performance
            self.collection.create_index([("feedback_id", pymongo.ASCENDING)], unique=True)
            self.collection.create_index([("feedback_source", pymongo.ASCENDING)])
            self.collection.create_index([("sentiment", pymongo.ASCENDING)])
            self.collection.create_index([("created_at", pymongo.DESCENDING)])
            
            self.logger.info("MongoDB connection established successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def save_analysis_result(self, result: FeedbackAnalysisResult) -> bool:
        """Save feedback analysis result to database"""
        try:
            # Convert to dictionary
            result_dict = result.to_dict()

            # Ensure _id is used as primary key (string UUID)
            if isinstance(result_dict.get("keywords"), str):
                result_dict["keywords"] = [result_dict["keywords"]]
            elif result_dict.get("keywords") is None:
                result_dict["keywords"] = []

            # Используем _id
            result_dict["_id"] = result.feedback_id
            result_dict.pop("feedback_id", None)

            self.collection.update_one(
                {"_id": result_dict["_id"]},
                {"$set": result_dict},
                upsert=True
            )

            self.logger.debug(f"Saved analysis result for feedback {result_dict['_id']}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save analysis result: {e}")
            return False
    
    def get_analysis_result(self, feedback_id: str) -> Optional[FeedbackAnalysisResult]:
        """Get analysis result by feedback ID"""
        try:
            result_dict = self.collection.find_one({"_id": feedback_id})

            if result_dict:
                # Restore feedback_id for domain model
                result_dict["feedback_id"] = result_dict["_id"]
                return FeedbackAnalysisResult.from_dict(result_dict)

            return None

        except Exception as e:
            self.logger.error(f"Failed to get analysis result: {e}")
            return None
    
    def get_analysis_history(self, feedback_source: Optional[str] = None, limit: int = 100) -> List[FeedbackAnalysisResult]:
        """Get analysis history with optional filtering"""
        try:
            # Build query
            query = {}
            if feedback_source:
                query["feedback_source"] = feedback_source
            
            # Execute query
            cursor = self.collection.find(query).sort("created_at", -1).limit(limit)
            
            results = []
            for result_dict in cursor:
                results.append(FeedbackAnalysisResult.from_dict(result_dict))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to get analysis history: {e}")
            return []
    
    def get_sentiment_statistics(self, feedback_source: Optional[str] = None) -> dict:
        """Get sentiment statistics using MongoDB aggregation"""
        try:
            # Build match stage
            match_stage = {}
            if feedback_source:
                match_stage["feedback_source"] = feedback_source
            
            # Aggregation pipeline
            pipeline = [
                {"$match": match_stage} if match_stage else {"$match": {}},
                {
                    "$group": {
                        "_id": "$sentiment",
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            # Execute aggregation
            sentiment_counts = list(self.collection.aggregate(pipeline))
            
            # Process results
            stats = {"positive": 0, "negative": 0, "neutral": 0}
            total = 0
            
            for item in sentiment_counts:
                sentiment = item["_id"]
                count = item["count"]
                stats[sentiment] = count
                total += count
            
            # Calculate percentages
            if total > 0:
                stats["total"] = total
                stats["positive_percentage"] = (stats["positive"] / total) * 100
                stats["negative_percentage"] = (stats["negative"] / total) * 100
                stats["neutral_percentage"] = (stats["neutral"] / total) * 100
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get sentiment statistics: {e}")
            return {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
    
    def delete_analysis_result(self, feedback_id: str) -> bool:
        """Delete analysis result by feedback ID"""
        try:
            result = self.collection.delete_one({"feedback_id": feedback_id})
            return result.deleted_count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to delete analysis result: {e}")
            return False
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.logger.info("MongoDB connection closed")
