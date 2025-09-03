"""
Test suite for the LLMApi class.

This module contains unit tests for the LLMApi class which handles interactions
with OpenAI-compatible LLM APIs.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from sokrates.llm_api import LLMApi
from sokrates.constants import Constants
import pytest


class TestLLMApi:
    """Test cases for the LLMApi class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.api_endpoint = pytest.TESTING_ENDPOINT
        self.api_key = "test_api_key"

    @patch('sokrates.llm_api.OpenAI')
    def test_init_with_custom_values(self, mock_openai):
        """Test initialization with custom values."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )

        assert api.api_endpoint == self.api_endpoint
        assert api.api_key == self.api_key

    @patch('sokrates.llm_api.OpenAI')
    def test_get_openai_client(self, mock_openai):
        """Test OpenAI client creation."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        result = api.get_openai_client()
        
        # Verify the OpenAI client was created with correct parameters
        mock_openai.assert_called_once_with(
            base_url=self.api_endpoint,
            api_key=self.api_key
        )
        assert result == mock_client_instance

    @patch('sokrates.llm_api.OpenAI')
    def test_list_models_success(self, mock_openai):
        """Test successful model listing."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Create a mock models response
        mock_model_1 = Mock()
        mock_model_1.id = "model-1"
        mock_model_2 = Mock()
        mock_model_2.id = "model-2"
        
        mock_models_response = Mock()
        mock_models_response.data = [mock_model_1, mock_model_2]
        mock_client_instance.models.list.return_value = mock_models_response
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        result = api.list_models()
        
        # Verify the call was made correctly
        mock_client_instance.models.list.assert_called_once()
        assert result == ["model-1", "model-2"]

    @patch('sokrates.llm_api.OpenAI')
    def test_list_models_exception(self, mock_openai):
        """Test model listing with exception."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Make the models.list call raise an exception
        mock_client_instance.models.list.side_effect = Exception("API Error")
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        with pytest.raises(Exception) as exc_info:
            api.list_models()
            
        assert "API Error" in str(exc_info.value)

    @patch('sokrates.llm_api.OpenAI')
    def test_send_with_context(self, mock_openai):
        """Test sending prompt with context."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Create a mock streaming response
        mock_chunk_1 = Mock()
        mock_chunk_1.choices = [Mock()]
        mock_chunk_1.choices[0].delta.content = "Hello"
        
        mock_chunk_2 = Mock()
        mock_chunk_2.choices = [Mock()]
        mock_chunk_2.choices[0].delta.content = " World"
        
        mock_stream_response = [mock_chunk_1, mock_chunk_2]
        mock_client_instance.chat.completions.create.return_value = mock_stream_response
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        # Test sending with context array
        result = api.send(
            prompt="Test prompt",
            model="test-model",
            context=["context1", "context2"],
            max_tokens=1000,
            temperature=0.7
        )
        
        # Verify the call was made correctly
        mock_client_instance.chat.completions.create.assert_called_once()
        assert result == "Hello World"

    @patch('sokrates.llm_api.OpenAI')
    def test_send_with_context(self, mock_openai):
        """Test sending prompt with context string."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Create a mock streaming response
        mock_chunk_1 = Mock()
        mock_chunk_1.choices = [Mock()]
        mock_chunk_1.choices[0].delta.content = "Response"
        
        mock_stream_response = [mock_chunk_1]
        mock_client_instance.chat.completions.create.return_value = mock_stream_response
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        # Test sending with context string
        result = api.send(
            prompt="Test prompt",
            model="test-model",
            context="context string",
            max_tokens=1000,
            temperature=0.7
        )
        
        # Verify the call was made correctly
        mock_client_instance.chat.completions.create.assert_called_once()
        assert result == "Response"

    @patch('sokrates.llm_api.OpenAI')
    def test_send_with_no_context(self, mock_openai):
        """Test sending prompt without context."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Create a mock streaming response
        mock_chunk_1 = Mock()
        mock_chunk_1.choices = [Mock()]
        mock_chunk_1.choices[0].delta.content = "Test"
        
        mock_stream_response = [mock_chunk_1]
        mock_client_instance.chat.completions.create.return_value = mock_stream_response
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        # Test sending without context
        result = api.send(
            prompt="Test prompt",
            model="test-model",
            max_tokens=1000,
            temperature=0.7
        )
        
        # Verify the call was made correctly
        mock_client_instance.chat.completions.create.assert_called_once()
        assert result == "Test"

    @patch('sokrates.llm_api.OpenAI')
    def test_send_exception_handling(self, mock_openai):
        """Test sending prompt with exception handling."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Make the chat.completions.create call raise an exception
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        with pytest.raises(Exception) as exc_info:
            api.send(
                prompt="Test prompt",
                model="test-model"
            )
            
        assert "API Error" in str(exc_info.value)

    @patch('sokrates.llm_api.OpenAI')
    def test_chat_completion(self, mock_openai):
        """Test chat completion functionality."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Create a mock streaming response
        mock_chunk_1 = Mock()
        mock_chunk_1.choices = [Mock()]
        mock_chunk_1.choices[0].delta.content = "Hello"
        
        mock_chunk_2 = Mock()
        mock_chunk_2.choices = [Mock()]
        mock_chunk_2.choices[0].delta.content = " World"
        
        mock_stream_response = [mock_chunk_1, mock_chunk_2]
        mock_client_instance.chat.completions.create.return_value = mock_stream_response
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        # Test chat completion
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        result = api.chat_completion(
            messages=messages,
            model="test-model",
            max_tokens=1000,
            temperature=0.7
        )
        
        # Verify the call was made correctly
        mock_client_instance.chat.completions.create.assert_called_once()
        assert result == "Hello World"

    @patch('sokrates.llm_api.OpenAI')
    def test_chat_completion_exception_handling(self, mock_openai):
        """Test chat completion with exception handling."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Make the chat.completions.create call raise an exception
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        
        with pytest.raises(Exception) as exc_info:
            api.chat_completion(messages=messages, model="test-model")
            
        assert "API Error" in str(exc_info.value)

    @patch('sokrates.llm_api.OpenAI')
    def test_combine_context(self, mock_openai):
        """Test context combination functionality."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        # Test combining context
        context_list = ["context1", "context2", "context3"]
        result = api.combine_context(context_list)
        
        # Verify the result format
        assert "---" in result  # Should contain separators
        assert len(result) > 0

    @patch('sokrates.llm_api.OpenAI')
    def test_send_with_default_model(self, mock_openai):
        """Test sending with default model from config."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_openai.return_value = mock_client_instance
        
        # Create a mock streaming response
        mock_chunk_1 = Mock()
        mock_chunk_1.choices = [Mock()]
        mock_chunk_1.choices[0].delta.content = "Response"
        
        mock_stream_response = [mock_chunk_1]
        mock_client_instance.chat.completions.create.return_value = mock_stream_response
        
        api = LLMApi(
            api_endpoint=self.api_endpoint,
            api_key=self.api_key
        )
        
        # Test sending without specifying model (should use default)
        result = api.send(prompt="Test prompt")
        
        # Verify the call was made with default model from config
        call_args = mock_client_instance.chat.completions.create.call_args[1]
        assert call_args['model'] == Constants.DEFAULT_MODEL
        assert result == "Response"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])