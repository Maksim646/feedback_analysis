#!/usr/bin/env python3
"""
NLP Worker Service Simulation Script
This script simulates sending feedback messages to the NLP Worker service
and displays the analysis results.

Usage:
    python3 simulate_nlp_worker.py
    python3 simulate_nlp_worker.py --interactive
    python3 simulate_nlp_worker.py --test-messages
"""

import sys
import os
import time
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Add the nlp_worker directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'proto', 'nlp_worker'))

try:
    import grpc
    from google.protobuf.timestamp_pb2 import Timestamp
    from proto.nlp_worker_reader import nlp_worker_reader_pb2, nlp_worker_reader_pb2_grpc
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure the NLP Worker service is properly installed.")
    print("Run: cd proto/nlp_worker && make install-clean")
    sys.exit(1)


class NlpWorkerSimulator:
    """Simulator for testing NLP Worker Service"""
    
    def __init__(self, host='localhost', port=5003):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.test_messages = self._get_test_messages()
    
    def _get_test_messages(self) -> List[Dict[str, Any]]:
        """Get predefined test messages for simulation"""
        return [
            {
                "id": "test_001",
                "source": "customer_support",
                "text": "I absolutely love this product! It exceeded all my expectations. The quality is outstanding and the customer service team was incredibly helpful. Five stars!",
                "expected_sentiment": "positive"
            },
            {
                "id": "test_002",
                "source": "app_store",
                "text": "This app is completely useless. It crashes every time I try to use it, the interface is confusing, and it's a total waste of money. Don't download this.",
                "expected_sentiment": "negative"
            },
            {
                "id": "test_003",
                "source": "website",
                "text": "The product arrived on time and was packaged well. It works as described, nothing special but gets the job done. Average experience overall.",
                "expected_sentiment": "neutral"
            },
            {
                "id": "test_004",
                "source": "social_media",
                "text": "Just tried the new feature and it's amazing! So much faster than before. Great job team! 🚀",
                "expected_sentiment": "positive"
            },
            {
                "id": "test_005",
                "source": "email",
                "text": "I'm very disappointed with the service. The response time is slow and the quality is poor. Not worth the money.",
                "expected_sentiment": "negative"
            },
            {
                "id": "test_006",
                "source": "survey",
                "text": "The product meets basic requirements. It's functional but could use some improvements. Overall satisfactory.",
                "expected_sentiment": "neutral"
            }
        ]
    
    def connect(self) -> bool:
        """Establish connection to NLP Worker service"""
        try:
            address = f"{self.host}:{self.port}"
            print(f"🔌 Connecting to NLP Worker service at {address}...")
            
            self.channel = grpc.insecure_channel(address)
            self.stub = nlp_worker_reader_pb2_grpc.NlpWorkerServiceStub(self.channel)
            
            # Test connection with a simple call
            print("✅ Connected successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            print("\n💡 Make sure the NLP Worker service is running:")
            print("   cd proto/nlp_worker")
            print("   make run")
            return False
    
    def disconnect(self):
        """Close connection to service"""
        if self.channel:
            self.channel.close()
            print("🔌 Connection closed")
    
    def analyze_feedback(self, feedback_id: str, source: str, text: str) -> Dict[str, Any]:
        """Send feedback to NLP Worker for analysis"""
        try:
            # Create timestamp
            timestamp = Timestamp()
            timestamp.FromDatetime(datetime.utcnow())
            
            # Create request
            request = nlp_worker_reader_pb2.CreateFeedbackAnalysisReq(
                feedback_id=feedback_id,
                feedback_source=source,
                text=text,
                created_at=timestamp
            )
            
            # Send request and measure time
            start_time = time.time()
            response = self.stub.CreateFeedbackAnalysis(request)
            duration = time.time() - start_time
            
            return {
                "success": True,
                "feedback_id": response.feedback_id,
                "sentiment": response.sentiment,
                "keywords": response.keywords,
                "response_time": duration,
                "timestamp": datetime.fromtimestamp(timestamp.seconds + timestamp.nanos / 1e9)
            }
            
        except grpc.RpcError as e:
            return {
                "success": False,
                "error": f"gRPC Error: {e.code()}: {e.details()}",
                "feedback_id": feedback_id
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "feedback_id": feedback_id
            }
    
    def run_test_messages(self):
        """Run predefined test messages"""
        print("\n🧪 Running predefined test messages...")
        print("=" * 80)
        
        results = []
        for i, message in enumerate(self.test_messages, 1):
            print(f"\n📝 Test {i}/{len(self.test_messages)}")
            print(f"   ID: {message['id']}")
            print(f"   Source: {message['source']}")
            print(f"   Text: {message['text'][:80]}...")
            print(f"   Expected: {message['expected_sentiment']}")
            
            # Analyze feedback
            result = self.analyze_feedback(
                message['id'],
                message['source'],
                message['text']
            )
            
            if result['success']:
                print(f"   ✅ Sentiment: {result['sentiment']}")
                print(f"   🔑 Keywords: {result['keywords']}")
                print(f"   ⏱️  Response time: {result['response_time']:.3f}s")
                
                # Check if sentiment matches expectation
                if result['sentiment'] == message['expected_sentiment']:
                    print("   🎯 Sentiment analysis: CORRECT!")
                else:
                    print(f"   ⚠️  Sentiment analysis: Expected {message['expected_sentiment']}, got {result['sentiment']}")
                
                results.append({
                    "id": message['id'],
                    "expected": message['expected_sentiment'],
                    "actual": result['sentiment'],
                    "correct": result['sentiment'] == message['expected_sentiment'],
                    "response_time": result['response_time']
                })
            else:
                print(f"   ❌ Failed: {result['error']}")
                results.append({
                    "id": message['id'],
                    "expected": message['expected_sentiment'],
                    "actual": "ERROR",
                    "correct": False,
                    "response_time": 0
                })
        
        # Summary
        self._print_summary(results)
    
    def _print_summary(self, results: List[Dict[str, Any]]):
        """Print test results summary"""
        print("\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        successful = [r for r in results if r['actual'] != 'ERROR']
        correct_sentiment = [r for r in successful if r['correct']]
        
        print(f"Total tests: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(results) - len(successful)}")
        
        if successful:
            avg_response_time = sum(r['response_time'] for r in successful) / len(successful)
            print(f"Average response time: {avg_response_time:.3f}s")
            print(f"Sentiment accuracy: {len(correct_sentiment)}/{len(successful)} ({len(correct_sentiment)/len(successful)*100:.1f}%)")
        
        print("\n🎯 Sentiment Analysis Results:")
        for result in results:
            status = "✅" if result['correct'] else "❌"
            print(f"   {status} {result['id']}: Expected {result['expected']}, Got {result['actual']}")
    
    def interactive_mode(self):
        """Run in interactive mode for custom messages"""
        print("\n💬 Interactive Mode - Enter your own feedback messages")
        print("Type 'quit' to exit, 'help' for commands")
        print("=" * 80)
        
        while True:
            try:
                # Get feedback text
                text = input("\n📝 Enter feedback text (or 'quit'/'help'): ").strip()
                
                if text.lower() == 'quit':
                    break
                elif text.lower() == 'help':
                    print("\n📚 Available commands:")
                    print("   quit - Exit interactive mode")
                    print("   help - Show this help")
                    print("   test - Run predefined test messages")
                    print("   clear - Clear screen")
                    continue
                elif text.lower() == 'test':
                    self.run_test_messages()
                    continue
                elif text.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                elif not text:
                    continue
                
                # Get source (optional)
                source = input("🏷️  Source (optional, press Enter for 'custom'): ").strip() or 'custom'
                
                # Generate ID
                feedback_id = f"interactive_{int(time.time())}"
                
                print(f"\n🔄 Analyzing feedback...")
                print(f"   ID: {feedback_id}")
                print(f"   Source: {source}")
                print(f"   Text: {text[:100]}{'...' if len(text) > 100 else ''}")
                
                # Analyze
                result = self.analyze_feedback(feedback_id, source, text)
                
                if result['success']:
                    print(f"\n✅ Analysis Complete!")
                    print(f"   Sentiment: {result['sentiment']}")
                    print(f"   Keywords: {result['keywords']}")
                    print(f"   Response time: {result['response_time']:.3f}s")
                else:
                    print(f"\n❌ Analysis Failed: {result['error']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting interactive mode...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    def run(self, mode='test'):
        """Run the simulator"""
        print("🚀 NLP Worker Service Simulator")
        print("=" * 50)
        
        if not self.connect():
            return
        
        try:
            if mode == 'interactive':
                self.interactive_mode()
            else:
                self.run_test_messages()
                
        finally:
            self.disconnect()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="NLP Worker Service Simulator")
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode for custom messages')
    parser.add_argument('--test-messages', '-t', action='store_true',
                       help='Run predefined test messages')
    parser.add_argument('--host', default='localhost', 
                       help='NLP Worker service host (default: localhost)')
    parser.add_argument('--port', type=int, default=5003,
                       help='NLP Worker service port (default: 5003)')
    
    args = parser.parse_args()
    
    # Determine mode
    if args.interactive:
        mode = 'interactive'
    elif args.test_messages:
        mode = 'test'
    else:
        mode = 'test'  # Default
    
    # Create and run simulator
    simulator = NlpWorkerSimulator(host=args.host, port=args.port)
    simulator.run(mode)


if __name__ == "__main__":
    main()
