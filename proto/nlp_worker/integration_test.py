#!/usr/bin/env python3
"""
Integration test for NLP Worker Service
Tests the complete flow from gRPC request to analysis result
"""

import grpc
import time
import json
import requests
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Import generated protobuf classes
from proto.nlp_worker_reader import nlp_worker_reader_pb2, nlp_worker_reader_pb2_grpc


class NlpWorkerIntegrationTest:
    """Integration test class for NLP Worker Service"""
    
    def __init__(self, grpc_host='localhost', grpc_port=5003, health_port=3003):
        self.grpc_host = grpc_host
        self.grpc_port = grpc_port
        self.health_port = health_port
        self.channel = None
        self.stub = None
        
    def setup(self):
        """Setup gRPC connection"""
        try:
            address = f"{self.grpc_host}:{self.grpc_port}"
            self.channel = grpc.insecure_channel(address)
            self.stub = nlp_worker_reader_pb2_grpc.NlpWorkerServiceStub(self.channel)
            print(f"✅ gRPC connection established to {address}")
            return True
        except Exception as e:
            print(f"❌ Failed to establish gRPC connection: {e}")
            return False
    
    def test_health_endpoints(self):
        """Test health check endpoints"""
        print("\n🔍 Testing health endpoints...")
        
        endpoints = [
            ("/ready", "Readiness"),
            ("/live", "Liveness"),
            ("/metrics", "Metrics")
        ]
        
        for endpoint, name in endpoints:
            try:
                url = f"http://localhost:{self.health_port}{endpoint}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"✅ {name} endpoint: OK")
                    if endpoint == "/metrics":
                        try:
                            metrics = response.json()
                            print(f"   📊 Metrics available: {list(metrics.keys())}")
                        except:
                            print(f"   📊 Metrics endpoint returned non-JSON response")
                else:
                    print(f"❌ {name} endpoint: HTTP {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {name} endpoint: Connection failed - {e}")
    
    def test_feedback_analysis(self):
        """Test feedback analysis functionality"""
        print("\n🧠 Testing feedback analysis...")
        
        test_cases = [
            {
                "id": "integration_001",
                "source": "customer_support",
                "text": "I absolutely love this product! It exceeded all my expectations. The quality is outstanding and the customer service team was incredibly helpful. Five stars!",
                "expected_sentiment": "positive"
            },
            {
                "id": "integration_002",
                "source": "app_store",
                "text": "This app is completely useless. It crashes every time I try to use it, the interface is confusing, and it's a total waste of money. Don't download this.",
                "expected_sentiment": "negative"
            },
            {
                "id": "integration_003",
                "source": "website",
                "text": "The product arrived on time and was packaged well. It works as described, nothing special but gets the job done. Average experience overall.",
                "expected_sentiment": "neutral"
            },
            {
                "id": "integration_004",
                "source": "social_media",
                "text": "Just tried the new feature and it's amazing! So much faster than before. Great job team! 🚀",
                "expected_sentiment": "positive"
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                print(f"\n📝 Testing: {test_case['id']}")
                print(f"   Source: {test_case['source']}")
                print(f"   Text: {test_case['text'][:80]}...")
                
                # Create timestamp
                timestamp = Timestamp()
                timestamp.FromDatetime(datetime.utcnow())
                
                # Create request
                request = nlp_worker_reader_pb2.CreateFeedbackAnalysisReq(
                    feedback_id=test_case["id"],
                    feedback_source=test_case["source"],
                    text=test_case["text"],
                    created_at=timestamp
                )
                
                # Make gRPC call
                start_time = time.time()
                response = self.stub.CreateFeedbackAnalysis(request)
                duration = time.time() - start_time
                
                print(f"   ⏱️  Response time: {duration:.3f}s")
                print(f"   😊 Sentiment: {response.sentiment}")
                print(f"   🔑 Keywords: {response.keywords}")
                
                # Check sentiment accuracy
                sentiment_correct = response.sentiment == test_case["expected_sentiment"]
                if sentiment_correct:
                    print("   ✅ Sentiment analysis correct!")
                else:
                    print(f"   ❌ Sentiment analysis incorrect. Expected: {test_case['expected_sentiment']}")
                
                # Check keywords
                keyword_count = len(response.keywords.split(',')) if response.keywords else 0
                if keyword_count > 0:
                    print(f"   ✅ Keywords extracted: {keyword_count}")
                else:
                    print("   ⚠️  No keywords extracted")
                
                results.append({
                    "id": test_case["id"],
                    "success": True,
                    "sentiment_correct": sentiment_correct,
                    "response_time": duration,
                    "keywords_count": keyword_count
                })
                
            except grpc.RpcError as e:
                print(f"   ❌ gRPC error: {e.code()}: {e.details()}")
                results.append({
                    "id": test_case["id"],
                    "success": False,
                    "error": f"{e.code()}: {e.details()}"
                })
            except Exception as e:
                print(f"   ❌ Unexpected error: {e}")
                results.append({
                    "id": test_case["id"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    def test_performance(self):
        """Test service performance with multiple requests"""
        print("\n⚡ Testing performance...")
        
        # Create a simple test request
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.utcnow())
        
        request = nlp_worker_reader_pb2.CreateFeedbackAnalysisReq(
            feedback_id="perf_test",
            feedback_source="performance_test",
            text="This is a performance test message to measure response times.",
            created_at=timestamp
        )
        
        # Run multiple requests
        num_requests = 10
        response_times = []
        
        print(f"   Running {num_requests} requests...")
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = self.stub.CreateFeedbackAnalysis(request)
                duration = time.time() - start_time
                response_times.append(duration)
                
                if (i + 1) % 5 == 0:
                    print(f"   Completed {i + 1}/{num_requests} requests")
                    
            except Exception as e:
                print(f"   ❌ Request {i + 1} failed: {e}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"   📊 Performance results:")
            print(f"      Average response time: {avg_time:.3f}s")
            print(f"      Min response time: {min_time:.3f}s")
            print(f"      Max response time: {max_time:.3f}s")
            print(f"      Total requests: {len(response_times)}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting NLP Worker Integration Tests")
        print("=" * 60)
        
        # Setup connection
        if not self.setup():
            print("❌ Cannot proceed without gRPC connection")
            return False
        
        # Run tests
        self.test_health_endpoints()
        results = self.test_feedback_analysis()
        self.test_performance()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 Test Summary")
        print("=" * 60)
        
        successful_tests = [r for r in results if r.get("success", False)]
        sentiment_correct = [r for r in successful_tests if r.get("sentiment_correct", False)]
        
        print(f"Total tests: {len(results)}")
        print(f"Successful: {len(successful_tests)}")
        print(f"Sentiment accuracy: {len(sentiment_correct)}/{len(successful_tests)} ({len(sentiment_correct)/len(successful_tests)*100:.1f}%)")
        
        if len(successful_tests) == len(results):
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        if self.channel:
            self.channel.close()


def main():
    """Main test runner"""
    test = NlpWorkerIntegrationTest()
    
    try:
        success = test.run_all_tests()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        exit_code = 1
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        exit_code = 1
    finally:
        test.cleanup()
    
    exit(exit_code)


if __name__ == "__main__":
    main()
