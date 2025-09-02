"""
Proxy Registration Endpoints
This module provides proxy registration endpoints for testing.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import time
import uuid
# In-memory registry for testing
_registry: Dict[str, Dict] = {}
router = APIRouter(prefix="/proxy", tags=["proxy"])
class ServerRegistration(BaseModel):
    """Server registration request model."""
    server_id: str
    server_url: str
    server_name: str
    description: Optional[str] = None
    version: Optional[str] = "1.0.0"
    capabilities: Optional[List[str]] = None
    endpoints: Optional[Dict[str, str]] = None
    auth_method: Optional[str] = "none"
    security_enabled: Optional[bool] = False
class ServerUnregistration(BaseModel):
    """Server unregistration request model."""
    server_key: str  # Use server_key directly
class HeartbeatData(BaseModel):
    """Heartbeat data model."""
    server_id: str
    server_key: str
    timestamp: Optional[int] = None
    status: Optional[str] = "healthy"
class RegistrationResponse(BaseModel):
    """Registration response model."""
    success: bool
    server_key: str
    message: str
    copy_number: int
class DiscoveryResponse(BaseModel):
    """Discovery response model."""
    success: bool
    servers: List[Dict]
    total: int
    active: int
@router.post("/register", response_model=RegistrationResponse)
async def register_server(registration: ServerRegistration):
    """Register a server with the proxy."""
    try:
        # Generate unique server key
        server_key = f"{registration.server_id}_{uuid.uuid4().hex[:8]}"
        copy_number = 1
        # Store server information
        _registry[server_key] = {
            "server_id": registration.server_id,
            "server_url": registration.server_url,
            "server_name": registration.server_name,
            "description": registration.description,
            "version": registration.version,
            "capabilities": registration.capabilities or [],
            "endpoints": registration.endpoints or {},
            "auth_method": registration.auth_method,
            "security_enabled": registration.security_enabled,
            "registered_at": int(time.time()),
            "last_heartbeat": int(time.time()),
            "status": "active"
        }
        return RegistrationResponse(
            success=True,
            server_key=server_key,
            message=f"Server {registration.server_name} registered successfully",
            copy_number=copy_number
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
@router.post("/unregister")
async def unregister_server(unregistration: ServerUnregistration):
    """Unregister a server from the proxy."""
    try:
        # Check if server exists in registry
        if unregistration.server_key not in _registry:
            raise HTTPException(status_code=404, detail="Server not found")
        # Remove from registry
        del _registry[unregistration.server_key]
        return {"success": True, "message": "Server unregistered successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unregistration failed: {str(e)}")
@router.post("/heartbeat")
async def send_heartbeat(heartbeat: HeartbeatData):
    """Send heartbeat for a registered server."""
    try:
        if heartbeat.server_key not in _registry:
            raise HTTPException(status_code=404, detail="Server not found")
        # Update heartbeat information
        _registry[heartbeat.server_key]["last_heartbeat"] = heartbeat.timestamp or int(time.time())
        _registry[heartbeat.server_key]["status"] = heartbeat.status
        return {"success": True, "message": "Heartbeat received"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heartbeat failed: {str(e)}")
@router.get("/discover", response_model=DiscoveryResponse)
async def discover_servers():
    """Discover active servers."""
    try:
        current_time = int(time.time())
        active_servers = []
        for server_key, server in _registry.items():
            # Consider server active if heartbeat was within last 5 minutes
            if current_time - server["last_heartbeat"] < 300:
                active_servers.append({
                    "server_key": server_key,
                    "server_id": server["server_id"],
                    "server_name": server["server_name"],
                    "server_url": server["server_url"],
                    "status": server["status"],
                    "last_heartbeat": server["last_heartbeat"]
                })
        return DiscoveryResponse(
            success=True,
            servers=active_servers,
            total=len(_registry),
            active=len(active_servers)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")
@router.get("/status")
async def get_proxy_status():
    """Get proxy status."""
    try:
        current_time = int(time.time())
        active_count = sum(
            1 for server in _registry.values()
            if current_time - server["last_heartbeat"] < 300
        )
        return {
            "success": True,
            "total_registered": len(_registry),
            "active_servers": active_count,
            "inactive_servers": len(_registry) - active_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
@router.delete("/clear")
async def clear_registry():
    """Clear the registry (for testing)."""
    try:
        _registry.clear()
        return {"success": True, "message": "Registry cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear failed: {str(e)}")
