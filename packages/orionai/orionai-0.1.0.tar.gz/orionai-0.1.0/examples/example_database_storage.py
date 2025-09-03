"""
AIPython Database & Storage Examples
====================================
Demonstrates 6 database and storage features.
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

def test_database_optimization():
    """Test database optimization techniques."""
    response = chat.database_optimization(
        "Create a sample database with performance issues and optimize "
        "queries, indexes, and schema design for better performance"
    )
    return response

def test_data_warehousing():
    """Test data warehouse design."""
    response = chat.data_warehousing(
        "Design a data warehouse for sales analytics with ETL pipelines, "
        "dimensional modeling, and data quality checks"
    )
    return response

def test_nosql_databases():
    """Test NoSQL database operations."""
    response = chat.nosql_databases(
        "Demonstrate operations with MongoDB for document storage, "
        "Redis for caching, and design patterns for NoSQL"
    )
    return response

def test_big_data_processing():
    """Test big data processing."""
    response = chat.big_data_processing(
        "Process a large dataset using Spark-like operations with "
        "distributed computing concepts and optimization techniques"
    )
    return response

def test_data_lake_management():
    """Test data lake architecture."""
    response = chat.data_lake_management(
        "Design a data lake architecture with data ingestion, "
        "cataloging, and governance for multiple data sources"
    )
    return response

def test_blockchain_storage():
    """Test blockchain operations."""
    response = chat.blockchain_storage(
        "Demonstrate blockchain interactions including wallet operations, "
        "transaction processing, and smart contract basics"
    )
    return response

if __name__ == "__main__":
    print("=== Database & Storage Features ===\n")
    
    # Test each feature
    features = [
        test_database_optimization,
        test_data_warehousing,
        test_nosql_databases,
        test_big_data_processing,
        test_data_lake_management,
        test_blockchain_storage
    ]
    
    for i, feature_test in enumerate(features, 1):
        print(f"{i}. Testing {feature_test.__name__}...")
        try:
            result = feature_test()
            print(f"✅ {feature_test.__name__} completed successfully\n")
        except Exception as e:
            print(f"❌ {feature_test.__name__} failed: {e}\n")
    
    print("=== Database & Storage Features Test Complete ===")
