"""
Middleware for request logging.
"""

import time
import json
import uuid
from typing import Callable, Awaitable, Dict, Any

from fastapi import Request, Response

from mcp_proxy_adapter.core.logging import logger, RequestLogger
from .base import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for logging requests and responses.
    """
    
    def __init__(self, app, config: Dict[str, Any] = None):
        """
        Initialize logging middleware.
        
        Args:
            app: FastAPI application
            config: Application configuration (optional)
        """
        super().__init__(app)
        self.config = config or {}
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Processes request and logs information about it.
        
        Args:
            request: Request.
            call_next: Next handler.
            
        Returns:
            Response.
        """
        # Generate unique ID for request
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Create context logger for this request
        req_logger = RequestLogger("mcp_proxy_adapter.api.middleware", request_id)
        
        # Log request start
        start_time = time.time()
        
        # Request information
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        
        # Check if this is an OpenAPI schema request (should be logged at DEBUG level)
        is_openapi_request = "/openapi.json" in url
        
        if is_openapi_request:
            req_logger.debug(f"Request started: {method} {url} | Client: {client_host}")
        else:
            req_logger.info(f"Request started: {method} {url} | Client: {client_host}")
        
        # Log request body if not GET or HEAD
        if method not in ["GET", "HEAD"]:
            try:
                body = await request.body()
                if body:
                    # Try to parse JSON
                    try:
                        body_text = body.decode("utf-8")
                        # Hide sensitive data (like passwords)
                        body_json = json.loads(body_text)
                        if isinstance(body_json, dict) and "params" in body_json:
                            # Replace sensitive fields with "***"
                            if isinstance(body_json["params"], dict):
                                for sensitive_field in ["password", "token", "secret", "api_key"]:
                                    if sensitive_field in body_json["params"]:
                                        body_json["params"][sensitive_field] = "***"
                        
                        req_logger.debug(f"Request body: {json.dumps(body_json)}")
                    except json.JSONDecodeError:
                        # If not JSON, log as is
                        req_logger.debug(f"Request body: {body_text}")
                    except Exception as e:
                        req_logger.warning(f"Error logging request body: {str(e)}")
            except Exception as e:
                req_logger.warning(f"Error reading request body: {str(e)}")
        
        # Call the next middleware or main handler
        try:
            response = await call_next(request)
            
            # Log request completion
            process_time = time.time() - start_time
            status_code = response.status_code
            
            if is_openapi_request:
                req_logger.debug(f"Request completed: {method} {url} | Status: {status_code} | "
                                f"Time: {process_time:.3f}s")
            else:
                req_logger.info(f"Request completed: {method} {url} | Status: {status_code} | "
                                f"Time: {process_time:.3f}s")
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"
            
            return response
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            
            if is_openapi_request:
                req_logger.debug(f"Request failed: {method} {url} | Error: {str(e)} | "
                                f"Time: {process_time:.3f}s")
            else:
                req_logger.error(f"Request failed: {method} {url} | Error: {str(e)} | "
                                f"Time: {process_time:.3f}s")
            
            raise 