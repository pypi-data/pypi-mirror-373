"""
Base middleware module.
"""

from typing import Callable, Awaitable
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response

from mcp_proxy_adapter.core.logging import logger

class BaseMiddleware(BaseHTTPMiddleware):
    """
    Base class for all middleware.
    """
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Method that will be overridden in child classes.
        
        Args:
            request: Request.
            call_next: Next handler.
            
        Returns:
            Response.
        """
        try:
            # Process request before calling the main handler
            await self.before_request(request)
            
            # Call the next middleware or main handler
            response = await call_next(request)
            
            # Process response after calling the main handler
            response = await self.after_response(request, response)
            
            return response
        except Exception as e:
            logger.exception(f"Error in middleware: {str(e)}")
            # If an error occurred, call the error handler
            return await self.handle_error(request, e)
    
    async def before_request(self, request: Request) -> None:
        """
        Method for processing request before calling the main handler.
        
        Args:
            request: Request.
        """
        pass
    
    async def after_response(self, request: Request, response: Response) -> Response:
        """
        Method for processing response after calling the main handler.
        
        Args:
            request: Request.
            response: Response.
            
        Returns:
            Processed response.
        """
        return response
    
    async def handle_error(self, request: Request, exception: Exception) -> Response:
        """
        Method for handling errors that occurred in middleware.
        
        Args:
            request: Request.
            exception: Exception.
            
        Returns:
            Error response.
        """
        # By default, just pass the error further
        raise exception 