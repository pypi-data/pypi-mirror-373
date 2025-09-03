"""
Unit tests for AIPython core functionality.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from orionai.python import AIPython


class TestAIPythonInitialization:
    """Test AIPython initialization."""
    
    def test_default_initialization(self, mock_api_key):
        """Test basic initialization with default parameters."""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': mock_api_key}):
            ai = AIPython()
            assert ai.provider_name == "google"
            assert ai.model_name == "gemini-1.5-pro"
            assert ai.verbose is True
    
    def test_custom_provider_initialization(self, mock_api_key):
        """Test initialization with custom provider."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': mock_api_key}):
            ai = AIPython(provider="openai", model="gpt-4")
            assert ai.provider_name == "openai"
            assert ai.model_name == "gpt-4"
    
    def test_invalid_provider_raises_error(self, mock_api_key):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            AIPython(provider="invalid_provider", api_key=mock_api_key)


class TestAIPythonBasicFunctionality:
    """Test basic AIPython functionality."""
    
    @patch('orionai.python.aipython.GoogleProvider')
    def test_ask_method(self, mock_provider_class, mock_api_key):
        """Test the ask method returns expected response."""
        # Setup mock
        mock_provider = Mock()
        mock_provider.generate.return_value = "print('Hello, World!')"
        mock_provider_class.return_value = mock_provider
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': mock_api_key}):
            ai = AIPython()
            result = ai.ask("Create a hello world program")
            
            assert result is not None
            mock_provider.generate.assert_called_once()
    
    def test_workspace_creation(self, temp_workspace, mock_api_key):
        """Test workspace directory creation."""
        with patch.dict('os.environ', {'GOOGLE_API_KEY': mock_api_key}):
            ai = AIPython(workspace_dir=temp_workspace)
            assert ai.workspace_dir == temp_workspace


class TestAIPythonErrorHandling:
    """Test error handling in AIPython."""
    
    @patch('orionai.python.aipython.GoogleProvider')
    def test_api_error_handling(self, mock_provider_class, mock_api_key):
        """Test handling of API errors."""
        # Setup mock to raise exception
        mock_provider = Mock()
        mock_provider.generate.side_effect = Exception("API Error")
        mock_provider_class.return_value = mock_provider
        
        with patch.dict('os.environ', {'GOOGLE_API_KEY': mock_api_key}):
            ai = AIPython()
            # Should handle error gracefully
            result = ai.ask("test query")
            # Verify error was handled (implementation dependent)
            mock_provider.generate.assert_called()


@pytest.mark.integration
class TestAIPythonIntegration:
    """Integration tests for AIPython (require actual API keys)."""
    
    @pytest.mark.skipif(
        not os.getenv('GOOGLE_API_KEY'),
        reason="Requires GOOGLE_API_KEY environment variable"
    )
    def test_real_api_call(self):
        """Test with real API call (requires API key)."""
        ai = AIPython()
        result = ai.ask("Calculate 2 + 2")
        assert result is not None
        assert len(result) > 0
