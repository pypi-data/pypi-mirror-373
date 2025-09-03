"""
Chat Completions Interface
"""

from typing import List, Dict, Any, Optional


class ChatCompletions:
    """
    Chat completions interface compatible with OpenAI API.
    """
    
    def __init__(self, client):
        """
        Initialize the chat completions interface.
        
        Args:
            client: The parent SentinelClient instance
        """
        self._client = client
        
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[Any, Any]:
        """
        Create a chat completion through the Sentinel gateway.
        
        Args:
            model (str): The model to use
            messages (list): List of message dictionaries
            temperature (float, optional): Sampling temperature
            max_tokens (int, optional): Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            dict: Chat completion response
        """
        data = {
            "model": model,
            "messages": messages
        }
        
        if temperature is not None:
            data["temperature"] = temperature
            
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
            
        # Add any additional parameters
        for key, value in kwargs.items():
            data[key] = value
            
        return self._client._make_request(
            method="POST",
            endpoint="/v1/chat/completions",
            data=data
        )