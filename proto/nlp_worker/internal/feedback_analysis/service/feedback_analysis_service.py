import logging
from datetime import datetime
from typing import List, Optional
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
import re
import sys

from internal.feedback_analysis.models.feedback_analysis import FeedbackAnalysisResult
from internal.feedback_analysis.repository.feedback_analysis_repository import FeedbackAnalysisRepository
from config.config import Config
from internal.metrics.nlp_worker_metrics import NlpWorkerMetrics


class FeedbackAnalysisService:
    def __init__(self, config: Config, metrics: NlpWorkerMetrics, logger: logging.Logger):
        self.config = config
        self.metrics = metrics
        self.logger = logger
        
        # Initialize NLP models
        self._initialize_nlp_models()
    
    def _initialize_nlp_models(self):
        """Initialize NLP models and download required NLTK data"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Try to load spaCy model (optional)
            self.nlp = None
            try:
                import spacy
                self.nlp = spacy.load(self.config.nlp.model_name)
                self.logger.info(f"spaCy model {self.config.nlp.model_name} loaded successfully")
            except (ImportError, OSError) as e:
                self.logger.warning(f"spaCy not available, using NLTK only: {e}")
                self.nlp = None
            
            # Initialize NLTK components
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            
            self.logger.info("NLP models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize NLP models: {e}")
            raise
    
    def analyze_feedback(self, feedback_id: str, feedback_source: str, text: str, created_at: datetime) -> FeedbackAnalysisResult:
        """Analyze feedback text and return sentiment and keywords"""
        try:
            self.logger.info(f"Starting analysis for feedback {feedback_id}")
            
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(text)
            
            # Extract sentiment
            sentiment = self._analyze_sentiment(cleaned_text)
            
            # Extract keywords
            keywords = self._extract_keywords(cleaned_text)
            
            # Create result
            result = FeedbackAnalysisResult(
                feedback_id=feedback_id,
                feedback_source=feedback_source,
                text=text,
                created_at=created_at,
                keywords=keywords,
                sentiment=sentiment,
                analyzed_at=datetime.utcnow()
            )
            
            # Save to repository
            # self.repository.save_analysis_result(result)
            
            self.logger.info(f"Analysis completed for feedback {feedback_id}: sentiment={sentiment}, keywords={keywords}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing feedback {feedback_id}: {e}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and extra whitespace
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment using TextBlob or fallback to simple rules"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Determine sentiment category
            if polarity > self.config.nlp.sentiment_threshold:
                return "positive"
            elif polarity < -self.config.nlp.sentiment_threshold:
                return "negative"
            else:
                return "neutral"
                
        except ImportError:
            # Fallback to simple rule-based sentiment analysis
            self.logger.warning("TextBlob not available, using rule-based sentiment analysis")
            return self._simple_sentiment_analysis(text)
        except Exception as e:
            self.logger.warning(f"Error in sentiment analysis: {e}")
            return "neutral"
    
    def _simple_sentiment_analysis(self, text: str) -> str:
        """Simple rule-based sentiment analysis as fallback"""
        positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'love', 'like', 'best', 'perfect', 'awesome'}
        negative_words = {'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'dislike', 'poor', 'useless', 'waste'}
        
        words = set(text.lower().split())
        positive_count = len(words.intersection(positive_words))
        negative_count = len(words.intersection(negative_words))
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_keywords(self, text: str) -> str:
        """Extract keywords using spaCy (if available) and NLTK"""
        try:
            keywords = []
            
            # Use spaCy if available
            if self.nlp:
                doc = self.nlp(text)
                for token in doc:
                    if (token.pos_ in ['NOUN', 'ADJ', 'VERB'] and 
                        not token.is_stop and 
                        len(token.text) > 2):
                        keywords.append(token.lemma_.lower())
            
            # Also use NLTK for additional keyword extraction
            tokens = word_tokenize(text)
            for token in tokens:
                if (len(token) > 2 and 
                    token.lower() not in self.stop_words and
                    token.isalpha()):
                    lemmatized = self.lemmatizer.lemmatize(token.lower())
                    if lemmatized not in keywords:
                        keywords.append(lemmatized)
            
            # Count frequency and get top keywords
            keyword_counts = Counter(keywords)
            top_keywords = [kw for kw, count in keyword_counts.most_common(self.config.nlp.max_keywords)]
            
            return ", ".join(top_keywords) if top_keywords else "no_keywords"
            
        except Exception as e:
            self.logger.warning(f"Error in keyword extraction: {e}")
            return "extraction_error"
    
    def get_analysis_history(self, feedback_source: Optional[str] = None, limit: int = 100) -> List[FeedbackAnalysisResult]:
        """Get analysis history with optional filtering"""
        return self.repository.get_analysis_history(feedback_source, limit)
    
    def get_sentiment_statistics(self, feedback_source: Optional[str] = None) -> dict:
        """Get sentiment statistics"""
        results = self.get_analysis_history(feedback_source)
        
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for result in results:
            sentiment_counts[result.sentiment] += 1
        
        total = len(results)
        if total > 0:
            sentiment_counts["total"] = total
            sentiment_counts["positive_percentage"] = (sentiment_counts["positive"] / total) * 100
            sentiment_counts["negative_percentage"] = (sentiment_counts["negative"] / total) * 100
            sentiment_counts["neutral_percentage"] = (sentiment_counts["neutral"] / total) * 100
        
        return sentiment_counts
