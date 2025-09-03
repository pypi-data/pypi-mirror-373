"""
AIPython Security & Encryption Examples
=======================================
Demonstrates 5 security and encryption features.
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

def test_cryptography_tools():
    """Test cryptography and encryption tools."""
    response = chat.cryptography_tools(
        "Demonstrate symmetric and asymmetric encryption, "
        "digital signatures, and secure key generation"
    )
    return response

def test_security_analysis():
    """Test security analysis and vulnerability scanning."""
    response = chat.security_analysis(
        "Perform security analysis on code and systems, "
        "identify vulnerabilities, and suggest security improvements"
    )
    return response

def test_password_security():
    """Test password security and authentication."""
    response = chat.password_security(
        "Generate secure passwords, implement password hashing, "
        "and demonstrate multi-factor authentication"
    )
    return response

def test_network_security():
    """Test network security monitoring."""
    response = chat.network_security(
        "Implement network scanning, intrusion detection, "
        "and traffic analysis for security monitoring"
    )
    return response

def test_data_privacy():
    """Test data privacy and anonymization."""
    response = chat.data_privacy(
        "Implement data anonymization, privacy-preserving techniques, "
        "and GDPR compliance features"
    )
    return response

if __name__ == "__main__":
    print("=== Security & Encryption Features ===\n")
    
    # Test each feature
    features = [
        test_cryptography_tools,
        test_security_analysis,
        test_password_security,
        test_network_security,
        test_data_privacy
    ]
    
    for i, feature_test in enumerate(features, 1):
        print(f"{i}. Testing {feature_test.__name__}...")
        try:
            result = feature_test()
            print(f"✅ {feature_test.__name__} completed successfully\n")
        except Exception as e:
            print(f"❌ {feature_test.__name__} failed: {e}\n")
    
    print("=== Security & Encryption Features Test Complete ===")
