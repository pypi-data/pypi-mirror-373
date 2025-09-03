"""
Sentinel Python SDK - A self-healing LLM firewall with cryptographic data protection
"""

from .client import SentinelClient
from .chat_completions import ChatCompletions

__version__ = "0.1.0"
__author__ = "Sentinel Team"
__all__ = ["SentinelClient", "ChatCompletions"]