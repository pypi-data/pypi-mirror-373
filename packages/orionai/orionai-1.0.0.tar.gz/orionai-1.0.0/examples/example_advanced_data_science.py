"""
AIPython Advanced Data Science Examples
=======================================
Demonstrates 10 advanced data science and analytics features.
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

def test_advanced_statistical_analysis():
    """Test comprehensive statistical analysis."""
    response = chat.advanced_statistical_analysis(
        "Load the sample data and perform comprehensive statistical analysis including "
        "distribution tests, outlier detection, and hypothesis testing"
    )
    return response

def test_automated_feature_engineering():
    """Test automated feature engineering."""
    response = chat.automated_feature_engineering(
        "Create a dataset with 1000 samples and automatically engineer features "
        "including polynomial, interaction, and time-based features"
    )
    return response

def test_time_series_forecasting():
    """Test advanced time series forecasting."""
    response = chat.time_series_forecasting(
        "Generate a time series with trend and seasonality, then forecast "
        "using ARIMA, Prophet, and LSTM models"
    )
    return response

def test_clustering_analysis():
    """Test comprehensive clustering analysis."""
    response = chat.clustering_analysis(
        "Create a 2D dataset with 500 points and apply multiple clustering algorithms "
        "including K-means, DBSCAN, and Gaussian Mixture Models"
    )
    return response

def test_anomaly_detection():
    """Test anomaly detection algorithms."""
    response = chat.anomaly_detection(
        "Generate a dataset with outliers and detect anomalies using "
        "Isolation Forest, One-Class SVM, and Local Outlier Factor"
    )
    return response

def test_survival_analysis():
    """Test survival analysis."""
    response = chat.survival_analysis(
        "Create a survival dataset and perform Kaplan-Meier analysis "
        "and Cox proportional hazards modeling"
    )
    return response

def test_causal_inference():
    """Test causal inference analysis."""
    response = chat.causal_inference(
        "Create a dataset with treatment and control groups and estimate "
        "treatment effects using propensity score matching"
    )
    return response

def test_bayesian_analysis():
    """Test Bayesian statistical analysis."""
    response = chat.bayesian_analysis(
        "Perform Bayesian linear regression with MCMC sampling "
        "and posterior analysis"
    )
    return response

def test_network_analysis():
    """Test network and graph analysis."""
    response = chat.network_analysis(
        "Create a social network graph and compute centrality measures, "
        "community detection, and network properties"
    )
    return response

def test_text_analytics_advanced():
    """Test advanced text analytics."""
    response = chat.text_analytics_advanced(
        "Create a text corpus and perform topic modeling, sentiment analysis, "
        "and document similarity analysis"
    )
    return response

if __name__ == "__main__":
    print("=== Advanced Data Science Features ===\n")
    
    # Test each feature
    features = [
        test_advanced_statistical_analysis,
        test_automated_feature_engineering,
        test_time_series_forecasting,
        test_clustering_analysis,
        test_anomaly_detection,
        test_survival_analysis,
        test_causal_inference,
        test_bayesian_analysis,
        test_network_analysis,
        test_text_analytics_advanced
    ]
    
    for i, feature_test in enumerate(features, 1):
        print(f"{i}. Testing {feature_test.__name__}...")
        try:
            result = feature_test()
            print(f"✅ {feature_test.__name__} completed successfully\n")
        except Exception as e:
            print(f"❌ {feature_test.__name__} failed: {e}\n")
    
    print("=== Data Science Features Test Complete ===")
