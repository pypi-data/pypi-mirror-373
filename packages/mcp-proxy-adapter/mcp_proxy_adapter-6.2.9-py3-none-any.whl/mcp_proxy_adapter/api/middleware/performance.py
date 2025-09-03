"""
Middleware for performance monitoring.
"""

import time
import statistics
from typing import Dict, List, Callable, Awaitable

from fastapi import Request, Response

from mcp_proxy_adapter.core.logging import logger
from .base import BaseMiddleware

class PerformanceMiddleware(BaseMiddleware):
    """
    Middleware for measuring performance.
    """
    
    def __init__(self, app):
        """
        Initializes performance middleware.
        
        Args:
            app: FastAPI application.
        """
        super().__init__(app)
        self.request_times: Dict[str, List[float]] = {}
        self.log_interval = 100  # Log statistics every 100 requests
        self.request_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Processes request and measures performance.
        
        Args:
            request: Request.
            call_next: Next handler.
            
        Returns:
            Response.
        """
        # Measure processing time
        start_time = time.time()
        
        # Call the next middleware or main handler
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Save time in statistics
        path = request.url.path
        if path not in self.request_times:
            self.request_times[path] = []
        
        self.request_times[path].append(process_time)
        
        # Logging statistics
        self.request_count += 1
        if self.request_count % self.log_interval == 0:
            self._log_stats()
        
        return response
    
    def _log_stats(self) -> None:
        """
        Logs performance statistics.
        """
        logger.info("Performance statistics:")
        
        for path, times in self.request_times.items():
            if len(times) > 1:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                # Calculate 95th percentile
                p95_time = sorted(times)[int(len(times) * 0.95)]
                
                logger.info(
                    f"Path: {path}, Requests: {len(times)}, "
                    f"Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, "
                    f"Max: {max_time:.3f}s, p95: {p95_time:.3f}s"
                ) 