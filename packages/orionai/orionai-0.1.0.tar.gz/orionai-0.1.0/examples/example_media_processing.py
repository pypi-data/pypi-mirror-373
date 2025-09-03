"""
AIPython Image & Media Processing Examples
==========================================
Demonstrates 6 image and media processing features.
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

def test_image_processing_advanced():
    """Test advanced image processing."""
    response = chat.image_processing_advanced(
        "Create and process images with advanced filtering, edge detection, "
        "morphological operations, and feature extraction"
    )
    return response

def test_video_processing():
    """Test video processing capabilities."""
    response = chat.video_processing(
        "Generate a sample video and demonstrate frame extraction, "
        "motion detection, and basic video editing operations"
    )
    return response

def test_audio_processing():
    """Test audio processing and analysis."""
    response = chat.audio_processing(
        "Generate audio samples and perform spectral analysis, "
        "noise reduction, and audio feature extraction"
    )
    return response

def test_pdf_processing():
    """Test PDF processing capabilities."""
    response = chat.pdf_processing(
        "Create a PDF document and demonstrate text extraction, "
        "image extraction, and PDF manipulation operations"
    )
    return response

def test_geospatial_analysis():
    """Test geospatial data analysis."""
    response = chat.geospatial_analysis(
        "Create geographic data and perform spatial analysis, "
        "distance calculations, and interactive mapping"
    )
    return response

def test_media_metadata():
    """Test media metadata processing."""
    response = chat.media_metadata(
        "Process media files to extract metadata, organize files, "
        "and perform content-based analysis"
    )
    return response

if __name__ == "__main__":
    print("=== Image & Media Processing Features ===\n")
    
    # Test each feature
    features = [
        test_image_processing_advanced,
        test_video_processing,
        test_audio_processing,
        test_pdf_processing,
        test_geospatial_analysis,
        test_media_metadata
    ]
    
    for i, feature_test in enumerate(features, 1):
        print(f"{i}. Testing {feature_test.__name__}...")
        try:
            result = feature_test()
            print(f"✅ {feature_test.__name__} completed successfully\n")
        except Exception as e:
            print(f"❌ {feature_test.__name__} failed: {e}\n")
    
    print("=== Image & Media Processing Features Test Complete ===")
