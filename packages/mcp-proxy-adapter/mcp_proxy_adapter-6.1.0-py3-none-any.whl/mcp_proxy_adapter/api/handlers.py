"""
Module with API request handlers.
"""

import json
import time
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.core.errors import (
    MicroserviceError, NotFoundError, ParseError, InvalidRequestError,
    MethodNotFoundError, InvalidParamsError, InternalError, CommandError
)
from mcp_proxy_adapter.core.logging import logger, RequestLogger, get_logger


async def execute_command(command_name: str, params: Dict[str, Any], request_id: Optional[str] = None, request: Optional[Request] = None) -> Dict[str, Any]:
    """
    Executes a command with the specified name and parameters.

    Args:
        command_name: Command name.
        params: Command parameters.
        request_id: Optional request identifier for logging context.

    Returns:
        Command execution result.

    Raises:
        MethodNotFoundError: If command is not found.
        MicroserviceError: In case of command execution error.
    """
    # Create request logger if request_id is provided
    log = RequestLogger(__name__, request_id) if request_id else logger
    
    try:
        log.info(f"Executing command: {command_name}")
        
        # Execute before command hooks
        try:
            from mcp_proxy_adapter.commands.hooks import hooks
            hooks.execute_before_command_hooks(command_name, params)
            log.debug(f"Executed before command hooks for: {command_name}")
        except Exception as e:
            log.warning(f"Failed to execute before command hooks: {e}")
        
        # Get command class from registry and execute with parameters
        start_time = time.time()
        
        # Use Command.run that handles instances with dependencies properly
        command_class = registry.get_command(command_name)
        
        # Create context with user info from request state
        context = {}
        if request and hasattr(request.state, 'user_id'):
            context['user'] = {
                'id': getattr(request.state, 'user_id', None),
                'role': getattr(request.state, 'user_role', 'guest'),
                'roles': getattr(request.state, 'user_roles', ['guest']),
                'permissions': getattr(request.state, 'user_permissions', ['read'])
            }
        
        result = await command_class.run(**params, context=context)
        
        execution_time = time.time() - start_time
        
        log.info(f"Command '{command_name}' executed in {execution_time:.3f} sec")
        
        # Execute after command hooks
        try:
            hooks.execute_after_command_hooks(command_name, params, result)
            log.debug(f"Executed after command hooks for: {command_name}")
        except Exception as e:
            log.warning(f"Failed to execute after command hooks: {e}")
        
        # Return result
        return result.to_dict()
    except NotFoundError as e:
        log.error(f"Command not found: {command_name}")
        # Преобразуем в MethodNotFoundError для соответствия JSON-RPC
        raise MethodNotFoundError(f"Method not found: {command_name}")
    except Exception as e:
        log.exception(f"Error executing command '{command_name}': {e}")
        if isinstance(e, MicroserviceError):
            raise e
        # Все остальные ошибки оборачиваем в InternalError
        raise InternalError(f"Error executing command: {str(e)}", data={"original_error": str(e)})


async def handle_batch_json_rpc(batch_requests: List[Dict[str, Any]], request: Optional[Request] = None) -> List[Dict[str, Any]]:
    """
    Handles batch JSON-RPC requests.

    Args:
        batch_requests: List of JSON-RPC request data.
        request: Original FastAPI request object.

    Returns:
        List of JSON-RPC responses.
    """
    responses = []
    
    # Get request_id from request state if available
    request_id = getattr(request.state, "request_id", None) if request else None
    
    for request_data in batch_requests:
        # Process each request in the batch
        response = await handle_json_rpc(request_data, request_id, request)
        responses.append(response)
    
    return responses


async def handle_json_rpc(request_data: Dict[str, Any], request_id: Optional[str] = None, request: Optional[Request] = None) -> Dict[str, Any]:
    """
    Handles JSON-RPC request.

    Args:
        request_data: JSON-RPC request data.
        request_id: Optional request identifier for logging context.

    Returns:
        JSON-RPC response.
    """
    # Create request logger if request_id is provided
    log = RequestLogger(__name__, request_id) if request_id else logger
    
    # Check JSON-RPC version
    if request_data.get("jsonrpc") != "2.0":
        return _create_error_response(
            InvalidRequestError("Invalid Request. Expected jsonrpc: 2.0"),
            request_data.get("id")
        )
    
    # Get method and parameters
    method = request_data.get("method")
    params = request_data.get("params", {})
    json_rpc_id = request_data.get("id")
    
    if not method:
        return _create_error_response(
            InvalidRequestError("Invalid Request. Method is required"),
            json_rpc_id
        )
    
    log.info(f"Executing JSON-RPC method: {method}")
    
    try:
        # Execute command
        result = await execute_command(method, params, request_id, request)
        
        # Form successful response
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": json_rpc_id
        }
    except MicroserviceError as e:
        # Method execution error
        log.error(f"Method execution error: {str(e)}")
        return _create_error_response(e, json_rpc_id)
    except Exception as e:
        # Internal server error
        log.exception(f"Unhandled error in JSON-RPC handler: {e}")
        return _create_error_response(
            InternalError("Internal error", data={"error": str(e)}),
            json_rpc_id
        )


def _create_error_response(error: MicroserviceError, request_id: Any) -> Dict[str, Any]:
    """
    Creates JSON-RPC error response.

    Args:
        error: Error object.
        request_id: Request ID from client.

    Returns:
        JSON-RPC error response dictionary.
    """
    return {
        "jsonrpc": "2.0",
        "error": error.to_dict(),
        "id": request_id
    }


async def get_server_health() -> Dict[str, Any]:
    """
    Gets server health information.

    Returns:
        Dictionary with server health information.
    """
    import os
    import platform
    import sys
    import psutil
    from datetime import datetime
    
    # Get process start time
    process = psutil.Process(os.getpid())
    start_time = datetime.fromtimestamp(process.create_time())
    uptime_seconds = (datetime.now() - start_time).total_seconds()
    
    # Get system information
    memory_info = process.memory_info()
    
    return {
        "status": "ok",
        "version": "1.0.0",  # Should be replaced with actual version
        "uptime": uptime_seconds,
        "components": {
            "system": {
                "python_version": sys.version,
                "platform": platform.platform(),
                "cpu_count": os.cpu_count()
            },
            "process": {
                "pid": os.getpid(),
                "memory_usage_mb": memory_info.rss / (1024 * 1024),
                "start_time": start_time.isoformat()
            },
            "commands": {
                "registered_count": len(registry.get_all_commands())
            }
        }
    }


async def get_commands_list() -> Dict[str, Dict[str, Any]]:
    """
    Gets list of available commands.

    Returns:
        Dictionary with information about available commands.
    """
    result = {}
    
    # Get all registered commands
    all_commands = registry.get_all_commands()
    
    for command_name, command_class in all_commands.items():
        # Get schema information for the command
        schema = command_class.get_schema()
        
        # Add to result
        result[command_name] = {
            "name": command_name,
            "schema": schema,
            "description": schema.get("description", "")
        }
    
    return result
