"""
Command catalog management system.

This module handles the command catalog, including:
- Loading commands from remote plugin servers
- Version comparison and updates
- Local command storage and management
- Automatic dependency installation
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from packaging import version as pkg_version

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.commands.dependency_manager import dependency_manager
from mcp_proxy_adapter.config import config

# Try to import requests, but don't fail if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests library not available, HTTP/HTTPS functionality will be limited")


class CommandCatalog:
    """
    Represents a command in the catalog with metadata.
    """
    
    def __init__(self, name: str, version: str, source_url: str, file_path: Optional[str] = None):
        self.name = name
        self.version = version
        self.source_url = source_url
        self.file_path = file_path
        self.metadata: Dict[str, Any] = {}
        
        # Standard metadata fields
        self.plugin: Optional[str] = None
        self.descr: Optional[str] = None
        self.category: Optional[str] = None
        self.author: Optional[str] = None
        self.email: Optional[str] = None
        self.depends: Optional[List[str]] = None  # New field for dependencies
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "source_url": self.source_url,
            "file_path": self.file_path,
            "plugin": self.plugin,
            "descr": self.descr,
            "category": self.category,
            "author": self.author,
            "email": self.email,
            "depends": self.depends,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandCatalog':
        """Create from dictionary."""
        catalog = cls(
            name=data["name"],
            version=data["version"],
            source_url=data["source_url"],
            file_path=data.get("file_path")
        )
        
        # Load standard metadata fields
        catalog.plugin = data.get("plugin")
        catalog.descr = data.get("descr")
        catalog.category = data.get("category")
        catalog.author = data.get("author")
        catalog.email = data.get("email")
        
        # Handle depends field
        depends = data.get("depends")
        if depends and isinstance(depends, list):
            catalog.depends = depends
        elif depends and isinstance(depends, str):
            catalog.depends = [depends]
        else:
            catalog.depends = depends
            
        catalog.metadata = data.get("metadata", {})
        
        return catalog


class CatalogManager:
    """
    Manages the command catalog system.
    
    The catalog is loaded fresh from servers each time - no caching.
    It only contains the list of available plugins.
    """
    
    def __init__(self, catalog_dir: str):
        """
        Initialize catalog manager.
        
        Args:
            catalog_dir: Directory to store downloaded command files
        """
        self.catalog_dir = Path(catalog_dir)
        self.commands_dir = self.catalog_dir / "commands"
        
        # Ensure directories exist
        self.catalog_dir.mkdir(parents=True, exist_ok=True)
        self.commands_dir.mkdir(parents=True, exist_ok=True)
        
        # No local catalog caching - always fetch fresh from servers
        self.catalog: Dict[str, CommandCatalog] = {}
    
    def _load_catalog(self) -> None:
        """DEPRECATED: Catalog is not cached locally."""
        logger.warning("_load_catalog() is deprecated - catalog is always fetched fresh from servers")
    
    def _save_catalog(self) -> None:
        """DEPRECATED: Catalog is not cached locally."""
        logger.warning("_save_catalog() is deprecated - catalog is always fetched fresh from servers")
    
    def _parse_catalog_data(self, server_catalog: Dict[str, Any], server_url: str = "http://example.com") -> Dict[str, CommandCatalog]:
        """
        Parse catalog data from server response.
        
        Args:
            server_catalog: Raw catalog data from server
            server_url: URL of the server (for constructing source URLs)
            
        Returns:
            Dictionary of parsed CommandCatalog objects
        """
        if not isinstance(server_catalog, dict):
            logger.error(f"Invalid catalog format: expected dict, got {type(server_catalog)}")
            return {}
        
        result = {}
        
        # Support both old format (commands array) and new format (id-value pairs)
        if "commands" in server_catalog:
            # Old format: {"commands": [{"name": "...", ...}]}
            commands_data = server_catalog.get("commands", [])
            
            if not isinstance(commands_data, list):
                logger.error(f"Invalid commands format: expected list, got {type(commands_data)}")
                return {}
            
            for cmd_data in commands_data:
                try:
                    if not isinstance(cmd_data, dict):
                        logger.warning(f"Skipping invalid command data: expected dict, got {type(cmd_data)}")
                        continue
                    
                    name = cmd_data.get("name")
                    if not name or not isinstance(name, str):
                        logger.warning(f"Skipping command without valid name")
                        continue
                    
                    version = cmd_data.get("version", "0.1")
                    if not isinstance(version, str):
                        logger.warning(f"Invalid version format for {name}: {version}")
                        version = "0.1"
                    
                    source_url = cmd_data.get("source_url", "")
                    if not isinstance(source_url, str):
                        logger.warning(f"Invalid source_url for {name}: {source_url}")
                        source_url = ""
                    
                    catalog = CommandCatalog(
                        name=name,
                        version=version,
                        source_url=source_url
                    )
                    
                    # Load standard metadata fields
                    catalog.plugin = cmd_data.get("plugin")
                    catalog.descr = cmd_data.get("descr")
                    catalog.category = cmd_data.get("category")
                    catalog.author = cmd_data.get("author")
                    catalog.email = cmd_data.get("email")
                    catalog.metadata = cmd_data
                    
                    result[name] = catalog
                    
                except Exception as e:
                    logger.error(f"Error processing command data: {e}")
                    continue
        else:
            # New format: {"id": {"plugin": "...", "descr": "...", ...}}
            for command_id, cmd_data in server_catalog.items():
                try:
                    if not isinstance(cmd_data, dict):
                        logger.warning(f"Skipping invalid command data for {command_id}: expected dict, got {type(cmd_data)}")
                        continue
                    
                    # Use command_id as name if name is not provided
                    name = cmd_data.get("name", command_id)
                    if not isinstance(name, str):
                        logger.warning(f"Skipping command {command_id} without valid name")
                        continue
                    
                    version = cmd_data.get("version", "0.1")
                    if not isinstance(version, str):
                        logger.warning(f"Invalid version format for {name}: {version}")
                        version = "0.1"
                    
                    # For new format, construct source_url from server_url and plugin filename
                    plugin_file = cmd_data.get("plugin")
                    if plugin_file and isinstance(plugin_file, str):
                        # Construct source URL by appending plugin filename to server URL
                        if server_url.endswith('/'):
                            source_url = f"{server_url}{plugin_file}"
                        else:
                            source_url = f"{server_url}/{plugin_file}"
                    else:
                        source_url = server_url
                    
                    catalog = CommandCatalog(
                        name=name,
                        version=version,
                        source_url=source_url
                    )
                    
                    # Load standard metadata fields
                    catalog.plugin = cmd_data.get("plugin")
                    catalog.descr = cmd_data.get("descr")
                    catalog.category = cmd_data.get("category")
                    catalog.author = cmd_data.get("author")
                    catalog.email = cmd_data.get("email")
                    
                    # Load dependencies field
                    depends = cmd_data.get("depends")
                    if depends and isinstance(depends, list):
                        catalog.depends = depends
                    elif depends and isinstance(depends, str):
                        # Handle case where depends is a single string
                        catalog.depends = [depends]
                    
                    # Store full metadata including new fields like "depends"
                    catalog.metadata = cmd_data
                    
                    result[name] = catalog
                    
                except Exception as e:
                    logger.error(f"Error processing command {command_id}: {e}")
                    continue
        
        return result

    def get_catalog_from_server(self, server_url: str) -> Dict[str, CommandCatalog]:
        """
        Fetch command catalog from remote server.
        
        Args:
            server_url: URL of the plugin server
            
        Returns:
            Dictionary of commands available on the server
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available, cannot fetch catalog from remote server")
            return {}
            
        try:
            # Validate URL format
            if not server_url.startswith(('http://', 'https://')):
                logger.error(f"Invalid server URL format: {server_url}")
                return {}
            
            # Fetch catalog from server (use URL as-is)
            logger.debug(f"Fetching catalog from: {server_url}")
            
            response = requests.get(server_url, timeout=30)
            response.raise_for_status()
            
            # Validate response content
            if not response.content:
                logger.error(f"Empty response from {server_url}")
                return {}
            
            try:
                server_catalog = response.json()
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from {server_url}: {e}")
                return {}
            
            if not isinstance(server_catalog, dict):
                logger.error(f"Invalid catalog format from {server_url}: expected dict, got {type(server_catalog)}")
                return {}
            
            result = self._parse_catalog_data(server_catalog, server_url)
            
            logger.info(f"Successfully fetched catalog from {server_url}: {len(result)} commands")
            return result
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching catalog from {server_url}")
            return {}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while fetching catalog from {server_url}: {e}")
            return {}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error while fetching catalog from {server_url}: {e}")
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while fetching catalog from {server_url}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error while fetching catalog from {server_url}: {e}")
            return {}
    
    def _check_dependencies(self, command_name: str, server_cmd: CommandCatalog) -> bool:
        """
        Check if command dependencies are satisfied.
        
        Args:
            command_name: Name of the command
            server_cmd: Command catalog entry from server
            
        Returns:
            True if dependencies are satisfied, False otherwise
        """
        if not server_cmd.depends:
            return True
        
        all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(server_cmd.depends)
        
        if not all_satisfied:
            logger.warning(f"Command {command_name} has missing dependencies: {missing_deps}")
            logger.info(f"Installed dependencies: {installed_deps}")
            return False
        
        logger.debug(f"All dependencies satisfied for command {command_name}: {server_cmd.depends}")
        return True
    
    def _install_dependencies(self, command_name: str, server_cmd: CommandCatalog, auto_install: bool = None) -> bool:
        """
        Install command dependencies automatically.
        
        Args:
            command_name: Name of the command
            server_cmd: Command catalog entry from server
            auto_install: Whether to automatically install missing dependencies (None = use config)
            
        Returns:
            True if all dependencies are satisfied, False otherwise
        """
        if not server_cmd.depends:
            return True
        
        # Use config setting if auto_install is None
        if auto_install is None:
            auto_install = config.get("commands.auto_install_dependencies", True)
        
        # Check current dependencies
        all_satisfied, missing_deps, installed_deps = dependency_manager.check_dependencies(server_cmd.depends)
        
        if all_satisfied:
            logger.info(f"All dependencies already satisfied for {command_name}: {server_cmd.depends}")
            return True
        
        if not auto_install:
            logger.warning(f"Command {command_name} has missing dependencies: {missing_deps}")
            logger.info(f"Auto-install is disabled. Please install manually: pip install {' '.join(missing_deps)}")
            return False
        
        # Try to install missing dependencies
        logger.info(f"Installing missing dependencies for {command_name}: {missing_deps}")
        
        success, installed_deps, failed_deps = dependency_manager.install_dependencies(missing_deps)
        
        if success:
            logger.info(f"Successfully installed all dependencies for {command_name}: {installed_deps}")
            
            # Verify installation
            all_verified, failed_verifications = dependency_manager.verify_installation(server_cmd.depends)
            if all_verified:
                logger.info(f"All dependencies verified for {command_name}")
                return True
            else:
                logger.error(f"Failed to verify dependencies for {command_name}: {failed_verifications}")
                return False
        else:
            logger.error(f"Failed to install dependencies for {command_name}: {failed_deps}")
            logger.error(f"Please install manually: pip install {' '.join(failed_deps)}")
            return False
    
    def _should_download_command(self, command_name: str, server_cmd: CommandCatalog) -> bool:
        """
        Check if command should be downloaded based on version comparison.
        
        Args:
            command_name: Name of the command
            server_cmd: Command catalog entry from server
            
        Returns:
            True if command should be downloaded, False otherwise
        """
        local_file = self.commands_dir / f"{command_name}_command.py"
        
        # If local file doesn't exist, download
        if not local_file.exists():
            logger.info(f"New command found: {command_name} v{server_cmd.version}")
            return True
        
        # Try to extract version from local file
        try:
            local_metadata = self.extract_metadata_from_file(str(local_file))
            local_version = local_metadata.get("version", "0.0")
            
            # Compare versions
            server_ver = pkg_version.parse(server_cmd.version)
            local_ver = pkg_version.parse(local_version)
            
            if server_ver > local_ver:
                logger.info(f"Newer version available for {command_name}: {local_ver} -> {server_ver}")
                return True
            else:
                logger.debug(f"Local version {local_ver} is same or newer than server version {server_ver}")
                return False
                
        except Exception as e:
            logger.warning(f"Failed to compare versions for {command_name}: {e}")
            # If version comparison fails, download anyway
            return True
    
    def update_command(self, command_name: str, server_catalog: Dict[str, CommandCatalog]) -> bool:
        """
        DEPRECATED: Always download fresh from server.
        
        Args:
            command_name: Name of the command to update
            server_catalog: Catalog from server
            
        Returns:
            True if command was downloaded, False otherwise
        """
        logger.warning("update_command() is deprecated - always downloading fresh from server (use _download_command directly)")
        
        if command_name not in server_catalog:
            return False
        
        server_cmd = server_catalog[command_name]
        return self._download_command(command_name, server_cmd)
    
    def _download_command(self, command_name: str, server_cmd: CommandCatalog) -> bool:
        """
        Download command file from server.
        
        Args:
            command_name: Name of the command
            server_cmd: Command catalog entry from server
            
        Returns:
            True if download successful, False otherwise
        """
        if not REQUESTS_AVAILABLE:
            logger.error("requests library not available, cannot download command from remote server")
            return False
        
        # Step 1: Check and install dependencies
        if not self._install_dependencies(command_name, server_cmd):
            logger.error(f"Cannot download {command_name}: failed to install dependencies")
            return False
            
        try:
            # Validate source URL
            if not server_cmd.source_url.startswith(('http://', 'https://')):
                logger.error(f"Invalid source URL for {command_name}: {server_cmd.source_url}")
                return False
            
            # Download command file (use source_url as-is)
            logger.debug(f"Downloading {command_name} from: {server_cmd.source_url}")
            
            response = requests.get(server_cmd.source_url, timeout=30)
            response.raise_for_status()
            
            # Validate response content
            if not response.content:
                logger.error(f"Empty response when downloading {command_name} from {server_cmd.source_url}")
                return False
            
            # Validate Python file content
            content = response.text
            if not content.strip():
                logger.error(f"Empty file content for {command_name} from {server_cmd.source_url}")
                return False
            
            # Basic Python file validation - only warn for clearly invalid files
            content_stripped = content.strip()
            if (content_stripped and 
                not content_stripped.startswith(('"""', "'''", '#', 'from ', 'import ', 'class ', 'def ')) and
                not any(keyword in content_stripped for keyword in ['class', 'def', 'import', 'from', '"""', "'''", '#'])):
                logger.warning(f"File {command_name}_command.py doesn't look like a valid Python file")
            
            # Create temporary file first for validation
            temp_file = None
            try:
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
                temp_file.write(content)
                temp_file.close()
                
                # Try to import the module to validate it
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(f"{command_name}_command", temp_file.name)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Check if module contains a Command class
                        if not hasattr(module, 'Command') and not any(
                            hasattr(module, attr) and attr.endswith('Command') 
                            for attr in dir(module)
                        ):
                            logger.warning(f"Module {command_name}_command.py doesn't contain a Command class")
                        
                except Exception as e:
                    logger.error(f"Failed to validate {command_name}_command.py: {e}")
                    return False
                
                # If validation passed, move to final location
                file_path = self.commands_dir / f"{command_name}_command.py"
                
                # Remove existing file if it exists
                if file_path.exists():
                    file_path.unlink()
                
                # Move temporary file to final location
                shutil.move(temp_file.name, file_path)
                
                # Update catalog entry
                server_cmd.file_path = str(file_path)
                self.catalog[command_name] = server_cmd
                
                # Extract metadata from downloaded file
                try:
                    metadata = self.extract_metadata_from_file(str(file_path))
                    if metadata:
                        # Update standard fields
                        if 'plugin' in metadata:
                            server_cmd.plugin = metadata['plugin']
                        if 'descr' in metadata:
                            server_cmd.descr = metadata['descr']
                        if 'category' in metadata:
                            server_cmd.category = metadata['category']
                        if 'author' in metadata:
                            server_cmd.author = metadata['author']
                        if 'email' in metadata:
                            server_cmd.email = metadata['email']
                        if 'version' in metadata:
                            server_cmd.version = metadata['version']
                        
                        # Update full metadata
                        server_cmd.metadata.update(metadata)
                        
                        logger.debug(f"Extracted metadata for {command_name}: {metadata}")
                except Exception as e:
                    logger.warning(f"Failed to extract metadata from {command_name}: {e}")
                
                logger.info(f"Successfully downloaded and validated {command_name} v{server_cmd.version}")
                return True
                
            finally:
                # Clean up temporary file if it still exists
                if temp_file and os.path.exists(temp_file.name):
                    try:
                        os.unlink(temp_file.name)
                    except Exception as e:
                        logger.warning(f"Failed to clean up temporary file {temp_file.name}: {e}")
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while downloading {command_name} from {server_cmd.source_url}")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error while downloading {command_name} from {server_cmd.source_url}: {e}")
            return False
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error while downloading {command_name} from {server_cmd.source_url}: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while downloading {command_name} from {server_cmd.source_url}: {e}")
            return False
        except OSError as e:
            logger.error(f"File system error while downloading {command_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while downloading {command_name}: {e}")
            return False
    
    def sync_with_servers(self, server_urls: List[str]) -> Dict[str, Any]:
        """
        Sync with remote servers - load fresh catalog each time.
        
        Args:
            server_urls: List of server URLs to sync with
            
        Returns:
            Dictionary with sync results
        """
        logger.info(f"Loading fresh catalog from {len(server_urls)} servers")
        
        # Clear local catalog - always start fresh
        self.catalog = {}
        
        results = {
            "servers_processed": 0,
            "commands_updated": 0,
            "commands_added": 0,
            "errors": []
        }
        
        for server_url in server_urls:
            try:
                # Get fresh catalog from server
                server_catalog = self.get_catalog_from_server(server_url)
                if not server_catalog:
                    continue
                
                results["servers_processed"] += 1
                
                # Process each command from server catalog
                for command_name, server_cmd in server_catalog.items():
                    # Check if we need to download/update
                    if self._should_download_command(command_name, server_cmd):
                        if self._download_command(command_name, server_cmd):
                            results["commands_added"] += 1
                            # Add to local catalog for this session
                            self.catalog[command_name] = server_cmd
                    else:
                        # Command already exists with same or newer version
                        logger.debug(f"Command {command_name} already exists with same or newer version")
                            
            except Exception as e:
                error_msg = f"Failed to sync with {server_url}: {e}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Fresh catalog loaded: {results}")
        return results
    
    def get_local_commands(self) -> List[str]:
        """
        Get list of locally available command files.
        
        Returns:
            List of command file paths
        """
        commands = []
        for file_path in self.commands_dir.glob("*_command.py"):
            commands.append(str(file_path))
        
        logger.debug(f"Found {len(commands)} local command files: {[Path(c).name for c in commands]}")
        return commands
    
    def get_command_info(self, command_name: str) -> Optional[CommandCatalog]:
        """
        Get information about a command in the catalog.
        
        Args:
            command_name: Name of the command
            
        Returns:
            Command catalog entry or None if not found
        """
        return self.catalog.get(command_name)
    
    def remove_command(self, command_name: str) -> bool:
        """
        Remove command from catalog and delete file.
        
        Args:
            command_name: Name of the command to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        if command_name not in self.catalog:
            return False
        
        try:
            # Remove file
            cmd = self.catalog[command_name]
            if cmd.file_path and os.path.exists(cmd.file_path):
                os.remove(cmd.file_path)
            
            # Remove from catalog
            del self.catalog[command_name]
            self._save_catalog()
            
            logger.info(f"Removed command: {command_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove command {command_name}: {e}")
            return False
    
    def extract_metadata_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from command file.
        
        Args:
            file_path: Path to command file
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for metadata in docstring or comments
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Look for metadata patterns
                if line.startswith('#') or line.startswith('"""') or line.startswith("'''"):
                    # Try to parse JSON-like metadata
                    if '{' in line and '}' in line:
                        try:
                            # Extract JSON part
                            start = line.find('{')
                            end = line.rfind('}') + 1
                            json_str = line[start:end]
                            
                            # Parse JSON
                            import json
                            parsed = json.loads(json_str)
                            
                            # Update metadata
                            metadata.update(parsed)
                            
                        except json.JSONDecodeError:
                            # Not valid JSON, continue
                            continue
                
                # Look for specific metadata patterns
                for pattern in ['plugin:', 'descr:', 'category:', 'author:', 'version:', 'email:']:
                    if pattern in line:
                        key = pattern.rstrip(':')
                        value = line.split(pattern, 1)[1].strip().strip('"\'')
                        metadata[key] = value
            
            # Also check for JSON in docstring blocks
            content_str = content
            if '"""' in content_str or "'''" in content_str:
                # Find docstring blocks
                import re
                docstring_pattern = r'"""(.*?)"""|\'\'\'(.*?)\'\'\''
                matches = re.findall(docstring_pattern, content_str, re.DOTALL)
                
                for match in matches:
                    docstring = match[0] if match[0] else match[1]
                    # Look for JSON in docstring
                    if '{' in docstring and '}' in docstring:
                        try:
                            # Find JSON object
                            start = docstring.find('{')
                            end = docstring.rfind('}') + 1
                            json_str = docstring[start:end]
                            
                            import json
                            parsed = json.loads(json_str)
                            metadata.update(parsed)
                            
                        except json.JSONDecodeError:
                            continue
            
            logger.debug(f"Extracted metadata from {file_path}: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return {}
    
    def update_local_command_metadata(self, command_name: str) -> bool:
        """
        Update metadata for a local command by reading its file.
        
        Args:
            command_name: Name of the command
            
        Returns:
            True if updated successfully, False otherwise
        """
        if command_name not in self.catalog:
            return False
        
        cmd = self.catalog[command_name]
        if not cmd.file_path or not os.path.exists(cmd.file_path):
            return False
        
        try:
            metadata = self.extract_metadata_from_file(cmd.file_path)
            
            if metadata:
                # Update standard fields
                if 'plugin' in metadata:
                    cmd.plugin = metadata['plugin']
                if 'descr' in metadata:
                    cmd.descr = metadata['descr']
                if 'category' in metadata:
                    cmd.category = metadata['category']
                if 'author' in metadata:
                    cmd.author = metadata['author']
                if 'email' in metadata:
                    cmd.email = metadata['email']
                if 'version' in metadata:
                    cmd.version = metadata['version']
                
                # Update full metadata
                cmd.metadata.update(metadata)
                
                # Save catalog
                self._save_catalog()
                
                logger.info(f"Updated metadata for {command_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update metadata for {command_name}: {e}")
            return False 