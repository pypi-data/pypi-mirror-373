"""
AIPython Advanced Machine Learning & AI Examples
================================================
Demonstrates 10 advanced ML and AI features.
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

def test_automl_pipeline():
    """Test automated machine learning pipeline."""
    response = chat.automl_pipeline(
        "Create an AutoML pipeline for binary classification with automated "
        "preprocessing, feature selection, and model optimization"
    )
    return response

def test_deep_learning_models():
    """Test deep learning model creation."""
    response = chat.deep_learning_models(
        "Build a CNN for image classification with data augmentation "
        "and transfer learning from a pre-trained model"
    )
    return response

def test_reinforcement_learning():
    """Test reinforcement learning algorithms."""
    response = chat.reinforcement_learning(
        "Implement Q-learning for a simple grid world environment "
        "with visualization of the learning process"
    )
    return response

def test_model_explainability():
    """Test model interpretation and explainability."""
    response = chat.model_explainability(
        "Train a random forest classifier and explain predictions using "
        "SHAP values and LIME explanations"
    )
    return response

def test_computer_vision():
    """Test computer vision capabilities."""
    response = chat.computer_vision(
        "Perform object detection on an image using YOLO or similar model "
        "and visualize the detected objects"
    )
    return response

def test_recommender_systems():
    """Test recommendation system algorithms."""
    response = chat.recommender_systems(
        "Build a movie recommendation system using collaborative filtering "
        "and matrix factorization techniques"
    )
    return response

def test_optimization_algorithms():
    """Test advanced optimization algorithms."""
    response = chat.optimization_algorithms(
        "Solve a traveling salesman problem using genetic algorithms "
        "and visualize the optimization process"
    )
    return response

def test_federated_learning():
    """Test federated learning implementation."""
    response = chat.federated_learning(
        "Simulate federated learning with multiple clients training "
        "a shared model while preserving privacy"
    )
    return response

def test_graph_neural_networks():
    """Test graph neural network models."""
    response = chat.graph_neural_networks(
        "Create a Graph Convolutional Network for node classification "
        "on a social network dataset"
    )
    return response

def test_quantum_ml():
    """Test quantum machine learning algorithms."""
    response = chat.quantum_ml(
        "Implement a variational quantum classifier using quantum circuits "
        "and compare with classical methods"
    )
    return response

if __name__ == "__main__":
    print("=== Advanced Machine Learning & AI Features ===\n")
    
    # Test each feature
    features = [
        test_automl_pipeline,
        test_deep_learning_models,
        test_reinforcement_learning,
        test_model_explainability,
        test_computer_vision,
        test_recommender_systems,
        test_optimization_algorithms,
        test_federated_learning,
        test_graph_neural_networks,
        test_quantum_ml
    ]
    
    for i, feature_test in enumerate(features, 1):
        print(f"{i}. Testing {feature_test.__name__}...")
        try:
            result = feature_test()
            print(f"✅ {feature_test.__name__} completed successfully\n")
        except Exception as e:
            print(f"❌ {feature_test.__name__} failed: {e}\n")
    
    print("=== Machine Learning & AI Features Test Complete ===")
