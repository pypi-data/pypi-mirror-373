"""
Sentinel Client Implementation
"""

import requests
from typing import Optional, Dict, Any
from .chat_completions import ChatCompletions


class SentinelClient:
    """
    Main client for interacting with the Sentinel gateway.
    
    The Sentinel client provides a secure interface to LLM providers
    through the Sentinel security pipeline.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the Sentinel client.
        
        Args:
            base_url (str): The base URL for the Sentinel gateway
            api_key (str, optional): API key for authentication
            timeout (int): Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.chat_completions = ChatCompletions(self)
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[Any, Any]] = None,
        params: Optional[Dict[Any, Any]] = None
    ) -> Dict[Any, Any]:
        """
        Make an HTTP request to the Sentinel gateway.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            data (dict, optional): Request data
            params (dict, optional): Query parameters
            
        Returns:
            dict: Response data
            
        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Sentinel-Python-SDK/0.1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            
        response = requests.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json() if response.content else {}
        
    def sanitize_prompt(self, prompt: str) -> Dict[Any, Any]:
        """
        Sanitize a prompt before sending to LLM.
        
        Args:
            prompt (str): The prompt to sanitize
            
        Returns:
            dict: Sanitized prompt and metadata
        """
        return self._make_request(
            method="POST",
            endpoint="/v1/sanitize",
            data={"prompt": prompt}
        )
        
    def process_response(self, response: str) -> Dict[Any, Any]:
        """
        Process an LLM response for security.
        
        Args:
            response (str): The LLM response to process
            
        Returns:
            dict: Processed response and metadata
        """
        return self._make_request(
            method="POST",
            endpoint="/v1/process",
            data={"response": response}
        )
        
    def configure_policies(self, policies: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Configure security policies.
        
        Args:
            policies (dict): Policy configuration
            
        Returns:
            dict: Policy update result
        """
        return self._make_request(
            method="POST",
            endpoint="/v1/policies",
            data={"policies": policies}
        )