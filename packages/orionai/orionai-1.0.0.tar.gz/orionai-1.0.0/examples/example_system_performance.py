"""
AIPython System & Performance Examples
======================================
Demonstrates 5 system and performance features.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orionai.python import AIPython

# Set your Google API key in environment variable
# os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'

chat = AIPython(
    provider="google",
    model="gemini-1.5-pro",
    verbose=True
)

def test_performance_optimization():
    """Test performance optimization techniques."""
    response = chat.performance_optimization(
        "Analyze code performance, implement optimization techniques, "
        "and provide benchmarking for improved efficiency"
    )
    return response

def test_system_monitoring():
    """Test system monitoring and resource tracking."""
    response = chat.system_monitoring(
        "Monitor system resources, track performance metrics, "
        "and implement real-time system health monitoring"
    )
    return response

def test_parallel_processing():
    """Test parallel and concurrent processing."""
    response = chat.parallel_processing(
        "Implement parallel processing using multiprocessing, "
        "threading, and async programming patterns"
    )
    return response

def test_memory_management():
    """Test memory management and optimization."""
    response = chat.memory_management(
        "Analyze memory usage, implement memory optimization, "
        "and demonstrate garbage collection monitoring"
    )
    return response

def test_cloud_integration():
    """Test cloud platform integration."""
    response = chat.cloud_integration(
        "Integrate with cloud services, implement cloud deployment, "
        "and demonstrate cloud resource management"
    )
    return response

if __name__ == "__main__":
    print("=== System & Performance Features ===\n")
    
    # Test each feature
    features = [
        test_performance_optimization,
        test_system_monitoring,
        test_parallel_processing,
        test_memory_management,
        test_cloud_integration
    ]
    
    for i, feature_test in enumerate(features, 1):
        print(f"{i}. Testing {feature_test.__name__}...")
        try:
            result = feature_test()
            print(f"✅ {feature_test.__name__} completed successfully\n")
        except Exception as e:
            print(f"❌ {feature_test.__name__} failed: {e}\n")
    
    print("=== System & Performance Features Test Complete ===")
