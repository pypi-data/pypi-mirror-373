"""
Tests for the Sentinel client
"""

import pytest
from unittest.mock import patch, Mock
from sentinel import SentinelClient


class TestSentinelClient:
    """Test cases for the SentinelClient class"""
    
    def test_init(self):
        """Test client initialization"""
        client = SentinelClient(
            base_url="http://test.example.com",
            api_key="test-key",
            timeout=60
        )
        
        assert client.base_url == "http://test.example.com"
        assert client.api_key == "test-key"
        assert client.timeout == 60
        
    def test_init_defaults(self):
        """Test client initialization with defaults"""
        client = SentinelClient()
        
        assert client.base_url == "http://localhost:8080"
        assert client.api_key is None
        assert client.timeout == 30
        
    @patch('sentinel.client.requests.request')
    def test_make_request(self, mock_request):
        """Test making HTTP requests"""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response
        
        client = SentinelClient(base_url="http://test.example.com")
        response = client._make_request("GET", "/test")
        
        assert response == {"test": "data"}
        mock_request.assert_called_once_with(
            method="GET",
            url="http://test.example.com/test",
            json=None,
            params=None,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Sentinel-Python-SDK/0.1.0"
            },
            timeout=30
        )
        
    @patch('sentinel.client.requests.request')
    def test_make_request_with_auth(self, mock_request):
        """Test making HTTP requests with authentication"""
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.content = b'{"test": "data"}'
        mock_request.return_value = mock_response
        
        client = SentinelClient(
            base_url="http://test.example.com",
            api_key="test-key"
        )
        response = client._make_request("GET", "/test")
        
        mock_request.assert_called_once_with(
            method="GET",
            url="http://test.example.com/test",
            json=None,
            params=None,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Sentinel-Python-SDK/0.1.0",
                "Authorization": "Bearer test-key"
            },
            timeout=30
        )
        
    @patch('sentinel.client.SentinelClient._make_request')
    def test_sanitize_prompt(self, mock_make_request):
        """Test prompt sanitization"""
        mock_make_request.return_value = {
            "sanitizedPrompt": "sanitized test",
            "detectedEntities": [],
            "policyViolations": [],
            "encryptionApplied": False
        }
        
        client = SentinelClient()
        result = client.sanitize_prompt("test prompt")
        
        assert result["sanitizedPrompt"] == "sanitized test"
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/sanitize",
            data={"prompt": "test prompt"}
        )
        
    @patch('sentinel.client.SentinelClient._make_request')
    def test_process_response(self, mock_make_request):
        """Test response processing"""
        mock_make_request.return_value = {
            "processedResponse": "processed test",
            "detectedEntities": [],
            "policyViolations": [],
            "encryptionApplied": False
        }
        
        client = SentinelClient()
        result = client.process_response("test response")
        
        assert result["processedResponse"] == "processed test"
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/process",
            data={"response": "test response"}
        )
        
    @patch('sentinel.client.SentinelClient._make_request')
    def test_configure_policies(self, mock_make_request):
        """Test policy configuration"""
        mock_make_request.return_value = {
            "success": True,
            "message": "Policies configured successfully"
        }
        
        client = SentinelClient()
        policies = {"test": "policy"}
        result = client.configure_policies(policies)
        
        assert result["success"] is True
        mock_make_request.assert_called_once_with(
            method="POST",
            endpoint="/v1/policies",
            data={"policies": {"test": "policy"}}
        )


if __name__ == "__main__":
    pytest.main([__file__])