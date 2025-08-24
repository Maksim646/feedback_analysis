#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test config
        from config.config import load_config
        print("✅ Config imports successfully")
        
        # Test models
        from internal.feedback_analysis.models.feedback_analysis import FeedbackAnalysisResult
        print("✅ Models import successfully")
        
        # Test repository
        from internal.feedback_analysis.repository.feedback_analysis_repository import FeedbackAnalysisRepository
        print("✅ Repository imports successfully")
        
        # Test service
        from internal.feedback_analysis.service.feedback_analysis_service import FeedbackAnalysisService
        print("✅ Service imports successfully")
        
        # Test metrics
        from internal.metrics.nlp_worker_metrics import NlpWorkerMetrics
        print("✅ Metrics import successfully")
        
        # Test gRPC service
        from internal.feedback_analysis.delivery.grpc.grpc_service import NlpWorkerGrpcService
        print("✅ gRPC service imports successfully")
        
        # Test server
        from internal.server.grpc_server import serve
        print("✅ Server imports successfully")
        
        # Test health server
        from internal.server.health_server import start_health_server
        print("✅ Health server imports successfully")
        
        # Test protobuf
        from proto.nlp_worker_reader import nlp_worker_reader_pb2, nlp_worker_reader_pb2_grpc
        print("✅ Protobuf imports successfully")
        
        print("\n🎉 All imports successful! The service is ready to run.")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
