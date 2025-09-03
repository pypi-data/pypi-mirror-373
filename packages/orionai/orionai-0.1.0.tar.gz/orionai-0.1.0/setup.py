"""
OrionAI Package Setup
====================
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core dependencies only
core_requirements = [
    "pandas>=1.5.0",
    "numpy>=1.21.0", 
    "requests>=2.25.0",
    "rich>=13.0.0",
    "google-generativeai>=0.3.0",
    "openai>=1.0.0",
    "anthropic>=0.3.0",
    "matplotlib>=3.5.0",
    "seaborn>=0.11.0",
    "scikit-learn>=1.0.0",
    "beautifulsoup4>=4.10.0",
    "flask>=2.0.0",
    "sqlalchemy>=1.4.0",
    "opencv-python>=4.5.0",
    "Pillow>=8.0.0",
    "cryptography>=3.4.0",
    "psutil>=5.8.0",
    "streamlit>=1.28.0",
    "python-dotenv>=0.19.0"
]

setup(
    name="orionai",
    version="0.1.0",
    author="AIMLDev726", 
    author_email="aistudentlearn4@gmail.com",
    description="AI-Powered Python Assistant with 50+ Advanced Features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AIMLDev726/OrionAI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Monitoring",
        "Topic :: Education",
        "Environment :: Web Environment",
        "Framework :: Streamlit"
    ],
    python_requires=">=3.8",
    install_requires=core_requirements,
    extras_require={
        "deep-learning": ["tensorflow>=2.8.0", "torch>=1.11.0"],
        "advanced-ml": ["xgboost>=1.5.0", "lightgbm>=3.2.0", "catboost>=1.0.0"],
        "web-advanced": ["selenium>=4.15.0", "scrapy>=2.5.0", "fastapi>=0.75.0"],
        "time-series": ["prophet>=1.0.0", "statsmodels>=0.13.0"],
        "cloud": ["boto3>=1.20.0", "google-cloud-storage>=2.0.0", "azure-storage-blob>=12.0.0"],
        "nlp": ["spacy>=3.4.0", "nltk>=3.7.0", "textblob>=0.17.0", "transformers>=4.20.0"],
        "visualization": ["plotly>=5.0.0", "dash>=2.0.0", "bokeh>=2.4.0"],
        "database": ["pymongo>=4.0.0", "redis>=4.0.0", "cassandra-driver>=3.29.0"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=4.0.0", "mypy>=0.950"],
        "all": [
            "tensorflow>=2.8.0", "torch>=1.11.0",
            "xgboost>=1.5.0", "lightgbm>=3.2.0",
            "selenium>=4.15.0", "scrapy>=2.5.0",
            "prophet>=1.0.0", "boto3>=1.20.0",
            "spacy>=3.4.0", "nltk>=3.7.0",
            "plotly>=5.0.0", "pymongo>=4.0.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "orionai-ui=orionai.python:ui",
        ],
    },
    keywords=[
        "ai", "machine-learning", "data-science", "automation", "llm",
        "python-assistant", "code-generation", "data-analysis", "visualization",
        "streamlit", "pandas", "scikit-learn", "openai", "gemini", "anthropic"
    ],
    project_urls={
        "Documentation": "https://github.com/AIMLDev726/OrionAI/tree/main/docs",
        "Source": "https://github.com/AIMLDev726/OrionAI",
        "Tracker": "https://github.com/AIMLDev726/OrionAI/issues",
    },
    include_package_data=True,
    zip_safe=False,
)
