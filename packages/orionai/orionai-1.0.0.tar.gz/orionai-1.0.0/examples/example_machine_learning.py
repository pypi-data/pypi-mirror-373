"""
AIPython Machine Learning Example
=================================
This example demonstrates machine learning capabilities including:
- Linear regression models
- Classification algorithms
- Clustering analysis
- Neural networks
- Dimensionality reduction
- Model evaluation
"""

import os
import sys
sys.path.append('..')
from orionai.python import AIPython

# Set your Google API key in environment variable
# os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'

chat = AIPython(
    provider="google",
    model="gemini-1.5-pro",
    verbose=True
)

# Test machine learning tasks
response = chat.ask("Create a simple linear regression model with sklearn using random data")

response = chat.ask("Generate a classification dataset and train a decision tree classifier")

response = chat.ask("Create a k-means clustering example with 3 clusters on 2D data")

response = chat.ask("Build a neural network with tensorflow/keras for binary classification")

response = chat.ask("Perform PCA dimensionality reduction on a sample dataset")

response = chat.ask("Create a confusion matrix and classification report for model evaluation")
