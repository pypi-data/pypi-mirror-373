"""
Test clients package for mcp_proxy_adapter.

This package contains test clients for testing various functionality
of the mcp_proxy_adapter, including security testing client.

Author: Vasiliy Zdanovskiy
Email: vasilyvz@gmail.com
"""

from .security_test_client import SecurityTestClient

__all__ = ["SecurityTestClient"]
