"""Full Application Example.

This example demonstrates advanced usage of MCP Proxy Adapter including:
- Proxy registration endpoints
- Custom command hooks
- Advanced security configurations
- Role-based access control
"""

from .main import get_app
app = get_app()
from .proxy_endpoints import router as proxy_router
