"""
AIPython Web Development & APIs Examples
========================================
Demonstrates 8 web development and API features.
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

def test_web_scraping_advanced():
    """Test advanced web scraping capabilities."""
    response = chat.web_scraping_advanced(
        "Create a web scraper that extracts product information from an e-commerce site "
        "with anti-detection measures and rate limiting"
    )
    return response

def test_api_development():
    """Test REST API development."""
    response = chat.api_development(
        "Build a REST API for a todo application with authentication, "
        "CRUD operations, and comprehensive error handling"
    )
    return response

def test_webhook_systems():
    """Test webhook creation and management."""
    response = chat.webhook_systems(
        "Create a webhook system that receives GitHub events and processes "
        "them with proper signature verification and retry logic"
    )
    return response

def test_microservices_architecture():
    """Test microservices design."""
    response = chat.microservices_architecture(
        "Design a microservices architecture for an e-commerce platform "
        "with user service, product service, and order service"
    )
    return response

def test_graphql_apis():
    """Test GraphQL API development."""
    response = chat.graphql_apis(
        "Create a GraphQL API for a blog platform with queries, mutations, "
        "and subscriptions for real-time updates"
    )
    return response

def test_websocket_systems():
    """Test WebSocket applications."""
    response = chat.websocket_systems(
        "Build a real-time chat application using WebSockets with "
        "room management and message broadcasting"
    )
    return response

def test_oauth_authentication():
    """Test OAuth authentication systems."""
    response = chat.oauth_authentication(
        "Implement OAuth 2.0 authentication with Google and GitHub providers "
        "including JWT tokens and refresh mechanisms"
    )
    return response

def test_api_testing_automation():
    """Test API testing frameworks."""
    response = chat.api_testing_automation(
        "Create an automated API testing suite with test data generation, "
        "response validation, and performance testing"
    )
    return response

if __name__ == "__main__":
    print("=== Web Development & API Features ===\n")
    
    # Test each feature
    features = [
        test_web_scraping_advanced,
        test_api_development,
        test_webhook_systems,
        test_microservices_architecture,
        test_graphql_apis,
        test_websocket_systems,
        test_oauth_authentication,
        test_api_testing_automation
    ]
    
    for i, feature_test in enumerate(features, 1):
        print(f"{i}. Testing {feature_test.__name__}...")
        try:
            result = feature_test()
            print(f"✅ {feature_test.__name__} completed successfully\n")
        except Exception as e:
            print(f"❌ {feature_test.__name__} failed: {e}\n")
    
    print("=== Web Development & API Features Test Complete ===")
