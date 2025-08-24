#!/usr/bin/env python3
"""
Simple test script for NLP Worker Service
"""

import grpc
import time
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Import generated protobuf classes
from proto.nlp_worker_reader import nlp_worker_reader_pb2, nlp_worker_reader_pb2_grpc


def test_feedback_analysis():
    """Test the feedback analysis functionality"""
    
    # Create gRPC channel
    channel = grpc.insecure_channel('localhost:5003')
    stub = nlp_worker_reader_pb2_grpc.NlpWorkerServiceStub(channel)
    
    # Test feedback texts
    test_feedbacks = [
        {
            "id": "test_001",
            "source": "customer_support",
            "text": "I love this product! It's amazing and works perfectly. The customer service is also excellent.",
            "expected_sentiment": "positive"
        },
        {
            "id": "test_002", 
            "source": "app_store",
            "text": "This app is terrible. It crashes constantly and the interface is confusing. Waste of money.",
            "expected_sentiment": "negative"
        },
        {
            "id": "test_003",
            "source": "website",
            "text": "The product arrived on time and was packaged well. It's okay, nothing special.",
            "expected_sentiment": "neutral"
        }
    ]
    
    print("Testing NLP Worker Service...")
    print("=" * 50)
    
    for feedback in test_feedbacks:
        try:
            # Create timestamp
            timestamp = Timestamp()
            timestamp.FromDatetime(datetime.utcnow())
            
            # Create request
            request = nlp_worker_reader_pb2.CreateFeedbackAnalysisReq(
                feedback_id=feedback["id"],
                feedback_source=feedback["source"],
                text=feedback["text"],
                created_at=timestamp
            )
            
            print(f"\nTesting feedback: {feedback['id']}")
            print(f"Source: {feedback['source']}")
            print(f"Text: {feedback['text'][:100]}...")
            print(f"Expected sentiment: {feedback['expected_sentiment']}")
            
            # Make gRPC call
            start_time = time.time()
            response = stub.CreateFeedbackAnalysis(request)
            duration = time.time() - start_time
            
            print(f"Response received in {duration:.2f}s")
            print(f"Actual sentiment: {response.sentiment}")
            print(f"Keywords: {response.keywords}")
            
            # Check if sentiment matches expectation
            if response.sentiment == feedback["expected_sentiment"]:
                print("✅ Sentiment analysis correct!")
            else:
                print(f"❌ Sentiment analysis incorrect. Expected: {feedback['expected_sentiment']}, Got: {response.sentiment}")
                
        except grpc.RpcError as e:
            print(f"❌ gRPC error: {e.code()}: {e.details()}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")


if __name__ == "__main__":
    test_feedback_analysis()
