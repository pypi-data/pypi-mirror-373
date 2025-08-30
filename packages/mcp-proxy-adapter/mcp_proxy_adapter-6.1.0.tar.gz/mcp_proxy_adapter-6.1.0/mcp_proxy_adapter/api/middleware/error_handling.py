"""
Middleware for error handling.
"""

import json
from typing import Callable, Awaitable, Dict, Any, Optional

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.core.errors import MicroserviceError, CommandError, ValidationError
from .base import BaseMiddleware

class ErrorHandlingMiddleware(BaseMiddleware):
    """
    Middleware for handling and formatting errors.
    """
    
    def __init__(self, app):
        """
        Initialize error handling middleware.
        
        Args:
            app: FastAPI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Processes request and catches errors.
        
        Args:
            request: Request.
            call_next: Next handler.
            
        Returns:
            Response.
        """
        try:
            # Call the next middleware or main handler
            return await call_next(request)
            
        except CommandError as e:
            # Command error
            request_id = getattr(request.state, "request_id", "unknown")
            logger.debug(f"[{request_id}] Command error: {str(e)}")
            
            # Проверяем, является ли запрос JSON-RPC
            is_jsonrpc = self._is_json_rpc_request(request)
            
            # Get JSON-RPC request ID if available
            request_id_jsonrpc = await self._get_json_rpc_id(request)
            
            # If request was JSON-RPC
            if is_jsonrpc:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": e.code,
                            "message": str(e),
                            "data": e.data if hasattr(e, "data") and e.data else None
                        },
                        "id": request_id_jsonrpc
                    }
                )
            
            # Regular API error
            return JSONResponse(
                status_code=400,
                content=e.to_dict()
            )
            
        except ValidationError as e:
            # Validation error
            request_id = getattr(request.state, "request_id", "unknown")
            logger.debug(f"[{request_id}] Validation error: {str(e)}")
            
            # Get JSON-RPC request ID if available
            request_id_jsonrpc = await self._get_json_rpc_id(request)
            
            # If request was JSON-RPC
            if self._is_json_rpc_request(request):
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32602,
                            "message": "Invalid params",
                            "data": e.data if hasattr(e, "data") and e.data else None
                        },
                        "id": request_id_jsonrpc
                    }
                )
            
            # Regular API error
            return JSONResponse(
                status_code=400,
                content=e.to_dict()
            )
            
        except MicroserviceError as e:
            # Other microservice error
            request_id = getattr(request.state, "request_id", "unknown")
            logger.debug(f"[{request_id}] Microservice error: {str(e)}")
            
            # Get JSON-RPC request ID if available
            request_id_jsonrpc = await self._get_json_rpc_id(request)
            
            # If request was JSON-RPC
            if self._is_json_rpc_request(request):
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32000,
                            "message": str(e),
                            "data": e.data if hasattr(e, "data") and e.data else None
                        },
                        "id": request_id_jsonrpc
                    }
                )
            
            # Regular API error
            return JSONResponse(
                status_code=400,
                content=e.to_dict()
            )
            
        except Exception as e:
            # Unexpected error
            request_id = getattr(request.state, "request_id", "unknown")
            logger.debug(f"[{request_id}] Unexpected error: {str(e)}")
            
            # Get JSON-RPC request ID if available
            request_id_jsonrpc = await self._get_json_rpc_id(request)
            
            # If request was JSON-RPC
            if self._is_json_rpc_request(request):
                return JSONResponse(
                    status_code=500,
                    content={
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Internal error"
                        },
                        "id": request_id_jsonrpc
                    }
                )
            
            # Regular API error
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": 500,
                        "message": "Internal server error"
                    }
                }
            )
    
    def _is_json_rpc_request(self, request: Request) -> bool:
        """
        Checks if request is a JSON-RPC request.
        
        Args:
            request: Request.
            
        Returns:
            True if request is JSON-RPC, False otherwise.
        """
        # Only requests to /api/jsonrpc are JSON-RPC requests
        return request.url.path == "/api/jsonrpc"
    
    async def _get_json_rpc_id(self, request: Request) -> Optional[Any]:
        """
        Gets JSON-RPC request ID.
        
        Args:
            request: Request.
            
        Returns:
            JSON-RPC request ID if available, None otherwise.
        """
        try:
            # Use request state to avoid body parsing if already done
            if hasattr(request.state, "json_rpc_id"):
                return request.state.json_rpc_id
                
            # Parse request body
            body = await request.body()
            if body:
                body_text = body.decode("utf-8")
                body_json = json.loads(body_text)
                request_id = body_json.get("id")
                
                # Save ID in request state to avoid reparsing
                request.state.json_rpc_id = request_id
                return request_id
        except Exception as e:
            logger.warning(f"Error parsing JSON-RPC ID: {str(e)}")
        
        return None 