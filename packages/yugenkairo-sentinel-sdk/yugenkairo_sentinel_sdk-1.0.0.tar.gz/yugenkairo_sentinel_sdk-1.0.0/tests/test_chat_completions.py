"""
Tests for the ChatCompletions class
"""

import pytest
from unittest.mock import patch, Mock
from sentinel import ChatCompletions, SentinelClient


class TestChatCompletions:
    """Test cases for the ChatCompletions class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = Mock(spec=SentinelClient)
        self.chat_completions = ChatCompletions(self.client)
        
    def test_init(self):
        """Test initialization"""
        assert self.chat_completions._client == self.client
        
    def test_create(self):
        """Test creating a chat completion"""
        self.client._make_request.return_value = {
            "id": "test-id",
            "choices": [{
                "message": {
                    "content": "test response"
                }
            }]
        }
        
        result = self.chat_completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "test"}]
        )
        
        assert result["id"] == "test-id"
        self.client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/chat/completions",
            data={
                "model": "test-model",
                "messages": [{"role": "user", "content": "test"}]
            }
        )
        
    def test_create_with_temperature(self):
        """Test creating a chat completion with temperature"""
        self.client._make_request.return_value = {
            "id": "test-id",
            "choices": [{
                "message": {
                    "content": "test response"
                }
            }]
        }
        
        result = self.chat_completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.7
        )
        
        self.client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/chat/completions",
            data={
                "model": "test-model",
                "messages": [{"role": "user", "content": "test"}],
                "temperature": 0.7
            }
        )
        
    def test_create_with_max_tokens(self):
        """Test creating a chat completion with max tokens"""
        self.client._make_request.return_value = {
            "id": "test-id",
            "choices": [{
                "message": {
                    "content": "test response"
                }
            }]
        }
        
        result = self.chat_completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=100
        )
        
        self.client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/chat/completions",
            data={
                "model": "test-model",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 100
            }
        )
        
    def test_create_with_additional_params(self):
        """Test creating a chat completion with additional parameters"""
        self.client._make_request.return_value = {
            "id": "test-id",
            "choices": [{
                "message": {
                    "content": "test response"
                }
            }]
        }
        
        result = self.chat_completions.create(
            model="test-model",
            messages=[{"role": "user", "content": "test"}],
            top_p=0.9,
            frequency_penalty=0.5
        )
        
        self.client._make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/chat/completions",
            data={
                "model": "test-model",
                "messages": [{"role": "user", "content": "test"}],
                "top_p": 0.9,
                "frequency_penalty": 0.5
            }
        )


if __name__ == "__main__":
    pytest.main([__file__])