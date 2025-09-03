"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Application Runner for MCP Proxy Adapter

This module provides the ApplicationRunner class for running applications
with full configuration validation and error handling.
"""

import socket
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastapi import FastAPI

from mcp_proxy_adapter.core.logging import get_logger

logger = get_logger("app_runner")


class ApplicationRunner:
    """
    Class for running applications with configuration validation.
    """
    
    def __init__(self, app: FastAPI, config: Dict[str, Any]):
        """
        Initialize ApplicationRunner.
        
        Args:
            app: FastAPI application instance
            config: Application configuration dictionary
        """
        self.app = app
        self.config = config
        self.errors: List[str] = []
        
    def validate_configuration(self) -> List[str]:
        """
        Validates configuration and returns list of errors.
        
        Returns:
            List of validation error messages
        """
        self.errors = []
        
        # Validate server configuration
        self._validate_server_config()
        
        # Validate SSL configuration
        self._validate_ssl_config()
        
        # Validate security configuration
        self._validate_security_config()
        
        # Validate file paths
        self._validate_file_paths()
        
        # Validate port availability
        self._validate_port_availability()
        
        # Validate configuration compatibility
        self._validate_compatibility()
        
        return self.errors
    
    def _validate_server_config(self) -> None:
        """Validate server configuration."""
        server_config = self.config.get("server", {})
        
        if not server_config:
            self.errors.append("Server configuration is missing")
            return
        
        host = server_config.get("host")
        port = server_config.get("port")
        
        if not host:
            self.errors.append("Server host is not specified")
        
        if not port:
            self.errors.append("Server port is not specified")
        elif not isinstance(port, int) or port < 1 or port > 65535:
            self.errors.append(f"Invalid server port: {port}")
    
    def _validate_ssl_config(self) -> None:
        """Validate SSL configuration."""
        ssl_config = self.config.get("ssl", {})
        
        if ssl_config.get("enabled", False):
            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            
            if not cert_file:
                self.errors.append("SSL enabled but certificate file not specified")
            elif not Path(cert_file).exists():
                self.errors.append(f"Certificate file not found: {cert_file}")
            
            if not key_file:
                self.errors.append("SSL enabled but private key file not specified")
            elif not Path(key_file).exists():
                self.errors.append(f"Private key file not found: {key_file}")
            
            # Validate mTLS configuration
            if ssl_config.get("verify_client", False):
                ca_cert = ssl_config.get("ca_cert")
                if not ca_cert:
                    self.errors.append("Client verification enabled but CA certificate not specified")
                elif not Path(ca_cert).exists():
                    self.errors.append(f"CA certificate file not found: {ca_cert}")
    
    def _validate_security_config(self) -> None:
        """Validate security configuration."""
        security_config = self.config.get("security", {})
        
        if security_config.get("enabled", False):
            auth_config = security_config.get("auth", {})
            permissions_config = security_config.get("permissions", {})
            
            # Validate authentication configuration
            if auth_config.get("enabled", False):
                methods = auth_config.get("methods", [])
                if not methods:
                    self.errors.append("Authentication enabled but no methods specified")
                
                # Validate API key configuration
                if "api_key" in methods:
                    # Check if roles file exists for API key auth
                    if permissions_config.get("enabled", False):
                        roles_file = permissions_config.get("roles_file")
                        if not roles_file:
                            self.errors.append("Permissions enabled but roles file not specified")
                        elif not Path(roles_file).exists():
                            self.errors.append(f"Roles file not found: {roles_file}")
                
                # Validate certificate configuration
                if "certificate" in methods:
                    ssl_config = self.config.get("ssl", {})
                    if not ssl_config.get("enabled", False):
                        self.errors.append("Certificate authentication requires SSL to be enabled")
                    if not ssl_config.get("verify_client", False):
                        self.errors.append("Certificate authentication requires client verification to be enabled")
    
    def _validate_file_paths(self) -> None:
        """Validate all file paths in configuration."""
        # Check SSL certificate files
        ssl_config = self.config.get("ssl", {})
        if ssl_config.get("enabled", False):
            cert_file = ssl_config.get("cert_file")
            key_file = ssl_config.get("key_file")
            ca_cert = ssl_config.get("ca_cert")
            
            if cert_file and not Path(cert_file).is_file():
                self.errors.append(f"Certificate file is not a regular file: {cert_file}")
            
            if key_file and not Path(key_file).is_file():
                self.errors.append(f"Private key file is not a regular file: {key_file}")
            
            if ca_cert and not Path(ca_cert).is_file():
                self.errors.append(f"CA certificate file is not a regular file: {ca_cert}")
        
        # Check roles file
        security_config = self.config.get("security", {})
        permissions_config = security_config.get("permissions", {})
        if permissions_config.get("enabled", False):
            roles_file = permissions_config.get("roles_file")
            if roles_file and not Path(roles_file).is_file():
                self.errors.append(f"Roles file is not a regular file: {roles_file}")
    
    def _validate_port_availability(self) -> None:
        """Validate that the configured port is available."""
        server_config = self.config.get("server", {})
        port = server_config.get("port")
        
        if port:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("127.0.0.1", port))
            except OSError:
                self.errors.append(f"Port {port} is already in use")
    
    def _validate_compatibility(self) -> None:
        """Validate configuration compatibility."""
        ssl_config = self.config.get("ssl", {})
        security_config = self.config.get("security", {})
        protocols_config = self.config.get("protocols", {})
        
        # Check SSL and protocol compatibility
        if ssl_config.get("enabled", False):
            allowed_protocols = protocols_config.get("allowed_protocols", [])
            if "http" in allowed_protocols and "https" not in allowed_protocols:
                self.errors.append("SSL enabled but HTTPS not in allowed protocols")
        
        # Check security and SSL compatibility
        if security_config.get("enabled", False):
            auth_config = security_config.get("auth", {})
            if auth_config.get("enabled", False):
                methods = auth_config.get("methods", [])
                if "certificate" in methods and not ssl_config.get("enabled", False):
                    self.errors.append("Certificate authentication requires SSL to be enabled")
    
    def setup_hooks(self) -> None:
        """
        Setup application hooks.
        """
        # Add startup event
        @self.app.on_event("startup")
        async def startup_event():
            logger.info("Application starting up")
            logger.info(f"Configuration validation passed with {len(self.errors)} errors")
        
        # Add shutdown event
        @self.app.on_event("shutdown")
        async def shutdown_event():
            logger.info("Application shutting down")
    
    def run(self) -> None:
        """
        Run application with full validation.
        """
        # Validate configuration
        errors = self.validate_configuration()
        
        if errors:
            print("ERROR: Configuration validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
        
        # Setup hooks
        self.setup_hooks()
        
        # Get server configuration
        server_config = self.config.get("server", {})
        host = server_config.get("host", "127.0.0.1")
        port = server_config.get("port", 8000)
        
        # Prepare server configuration for hypercorn
        server_kwargs = {
            "host": host,
            "port": port,
            "log_level": "info"
        }
        
        # Add SSL configuration if enabled
        ssl_config = self.config.get("ssl", {})
        if ssl_config.get("enabled", False):
            server_kwargs["certfile"] = ssl_config.get("cert_file")
            server_kwargs["keyfile"] = ssl_config.get("key_file")
            
            # Add mTLS configuration if enabled
            if ssl_config.get("verify_client", False):
                server_kwargs["ca_certs"] = ssl_config.get("ca_cert")
        
        try:
            import hypercorn.asyncio
            import asyncio
            
            print(f"🚀 Starting server on {host}:{port}")
            print("   Use Ctrl+C to stop the server")
            print("=" * 60)
            
            # Run with hypercorn
            asyncio.run(hypercorn.asyncio.serve(self.app, **server_kwargs))
            
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"\n❌ Failed to start server: {e}", file=sys.stderr)
            sys.exit(1)
