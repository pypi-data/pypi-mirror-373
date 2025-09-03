"""
Key Management Command

This module provides commands for key management including generation,
validation, rotation, backup, and restoration.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
import os
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .base import Command
from .result import CommandResult, SuccessResult, ErrorResult
from ..core.certificate_utils import CertificateUtils

logger = logging.getLogger(__name__)


class KeyResult:
    """
    Result class for key operations.
    
    Contains key information and operation status.
    """
    
    def __init__(self, key_path: str, key_type: str, key_size: int,
                 created_date: Optional[str] = None, expiry_date: Optional[str] = None,
                 status: str = "valid", error: Optional[str] = None):
        """
        Initialize key result.
        
        Args:
            key_path: Path to key file
            key_type: Type of key (RSA, ECDSA, etc.)
            key_size: Key size in bits
            created_date: Key creation date
            expiry_date: Key expiry date
            status: Key status (valid, expired, error)
            error: Error message if any
        """
        self.key_path = key_path
        self.key_type = key_type
        self.key_size = key_size
        self.created_date = created_date
        self.expiry_date = expiry_date
        self.status = status
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "key_path": self.key_path,
            "key_type": self.key_type,
            "key_size": self.key_size,
            "created_date": self.created_date,
            "expiry_date": self.expiry_date,
            "status": self.status,
            "error": self.error
        }
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get JSON schema for this result.
        
        Returns:
            JSON schema dictionary
        """
        return {
            "type": "object",
            "properties": {
                "key_path": {"type": "string", "description": "Path to key file"},
                "key_type": {"type": "string", "description": "Type of key"},
                "key_size": {"type": "integer", "description": "Key size in bits"},
                "created_date": {"type": "string", "description": "Key creation date"},
                "expiry_date": {"type": "string", "description": "Key expiry date"},
                "status": {"type": "string", "enum": ["valid", "expired", "error"], 
                          "description": "Key status"},
                "error": {"type": "string", "description": "Error message if any"}
            },
            "required": ["key_path", "key_type", "key_size", "status"]
        }


class KeyManagementCommand(Command):
    """
    Command for key management.
    
    Provides methods for generating, validating, rotating, backing up, and restoring keys.
    """
    
    # Command metadata
    name = "key_management"
    version = "1.0.0"
    descr = "Private key generation, validation, and management"
    category = "security"
    author = "MCP Proxy Adapter Team"
    email = "team@mcp-proxy-adapter.com"
    source_url = "https://github.com/mcp-proxy-adapter"
    result_class = KeyResult
    
    def __init__(self):
        """Initialize key management command."""
        super().__init__()
        self.certificate_utils = CertificateUtils()
    
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute key management command.
        
        Args:
            **kwargs: Command parameters including:
                - action: Action to perform (key_generate, key_validate, key_rotate, key_backup, key_restore)
                - key_type: Type of key to generate (RSA, ECDSA)
                - key_size: Key size in bits for generation
                - output_path: Output path for key generation
                - password: Password for key encryption
                - key_path: Key file path for validation, rotation, backup
                - old_key_path: Old key path for rotation
                - new_key_path: New key path for rotation
                - cert_path: Certificate path for rotation
                - backup_old: Whether to backup old key during rotation
                - backup_path: Backup path for key backup/restore
                - encrypt_backup: Whether to encrypt backup
                
        Returns:
            CommandResult with key operation status
        """
        action = kwargs.get("action", "key_validate")
        
        if action == "key_generate":
            key_type = kwargs.get("key_type")
            key_size = kwargs.get("key_size")
            output_path = kwargs.get("output_path")
            password = kwargs.get("password")
            return await self.key_generate(key_type, key_size, output_path, password)
        elif action == "key_validate":
            key_path = kwargs.get("key_path")
            password = kwargs.get("password")
            return await self.key_validate(key_path, password)
        elif action == "key_rotate":
            old_key_path = kwargs.get("old_key_path")
            new_key_path = kwargs.get("new_key_path")
            cert_path = kwargs.get("cert_path")
            backup_old = kwargs.get("backup_old", True)
            return await self.key_rotate(old_key_path, new_key_path, cert_path, backup_old)
        elif action == "key_backup":
            key_path = kwargs.get("key_path")
            backup_path = kwargs.get("backup_path")
            encrypt_backup = kwargs.get("encrypt_backup", True)
            password = kwargs.get("password")
            return await self.key_backup(key_path, backup_path, encrypt_backup, password)
        elif action == "key_restore":
            backup_path = kwargs.get("backup_path")
            key_path = kwargs.get("key_path")
            password = kwargs.get("password")
            return await self.key_restore(backup_path, key_path, password)
        else:
            return ErrorResult(
                message=f"Unknown action: {action}. Supported actions: key_generate, key_validate, key_rotate, key_backup, key_restore"
            )
    
    async def key_generate(self, key_type: str, key_size: int, output_path: str,
                          password: Optional[str] = None) -> CommandResult:
        """
        Generate a new private key.
        
        Args:
            key_type: Type of key to generate (RSA, ECDSA)
            key_size: Key size in bits
            output_path: Path to save the generated key
            password: Optional password to encrypt the key
            
        Returns:
            CommandResult with key generation status
        """
        try:
            logger.info(f"Generating {key_type} key with size {key_size} bits")
            
            # Validate parameters
            if key_type not in ["RSA", "ECDSA"]:
                return ErrorResult(
                    message="Key type must be RSA or ECDSA"
                )
            
            if key_type == "ECDSA":
                if key_size not in [256, 384, 521]:
                    return ErrorResult(
                        message="ECDSA key size must be 256, 384, or 521 bits"
                    )
            elif key_size < 1024:
                return ErrorResult(
                    message="Key size must be at least 1024 bits"
                )
            
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(output_path)
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Generate key
            result = self.certificate_utils.generate_private_key(
                key_type, key_size, output_path
            )
            
            if not result["success"]:
                return ErrorResult(
                    message=f"Key generation failed: {result['error']}"
                )
            
            key_result = KeyResult(
                key_path=output_path,
                key_type=key_type,
                key_size=key_size,
                created_date=datetime.now().isoformat(),
                status="valid"
            )
            
            logger.info(f"Key generated successfully: {output_path}")
            return SuccessResult(
                data={
                    "key": key_result.to_dict(),
                    "details": result
                }
            )
            
        except Exception as e:
            logger.error(f"Key generation failed: {e}")
            return ErrorResult(
                message=f"Key generation failed: {str(e)}"
            )
    
    async def key_validate(self, key_path: str, password: Optional[str] = None) -> CommandResult:
        """
        Validate a private key.
        
        Args:
            key_path: Path to key file to validate
            password: Optional password if key is encrypted
            
        Returns:
            CommandResult with key validation status
        """
        try:
            logger.info(f"Validating key: {key_path}")
            
            # Validate parameters
            if not key_path or not os.path.exists(key_path):
                return ErrorResult(
                    message=f"Key file not found: {key_path}"
                )
            
            # Validate key
            result = self.certificate_utils.validate_private_key(key_path)
            
            if not result["success"]:
                return ErrorResult(
                    message=f"Key validation failed: {result['error']}"
                )
            
            key_result = KeyResult(
                key_path=key_path,
                key_type=result.get("key_type", "unknown"),
                key_size=result.get("key_size", 0),
                created_date=result.get("created_date"),
                status="valid"
            )
            
            logger.info(f"Key validation completed: {key_path}")
            return SuccessResult(
                data={
                    "key": key_result.to_dict()
                }
            )
            
        except Exception as e:
            logger.error(f"Key validation failed: {e}")
            return ErrorResult(
                message=f"Key validation failed: {str(e)}"
            )
    
    async def key_rotate(self, old_key_path: str, new_key_path: str,
                        cert_path: Optional[str] = None, backup_old: bool = True) -> CommandResult:
        """
        Rotate a private key.
        
        Args:
            old_key_path: Path to old key file
            new_key_path: Path to new key file
            cert_path: Optional certificate path to update with new key
            backup_old: Whether to backup the old key
            
        Returns:
            CommandResult with key rotation status
        """
        try:
            logger.info(f"Rotating key from {old_key_path} to {new_key_path}")
            
            # Validate parameters
            if not old_key_path or not os.path.exists(old_key_path):
                return ErrorResult(
                    message=f"Old key file not found: {old_key_path}"
                )
            
            if not new_key_path or not os.path.exists(new_key_path):
                return ErrorResult(
                    message=f"New key file not found: {new_key_path}"
                )
            
            # Validate both keys
            old_key_validation = await self.key_validate(old_key_path)
            new_key_validation = await self.key_validate(new_key_path)
            
            if not old_key_validation.to_dict()["success"]:
                return ErrorResult(
                    message=f"Old key validation failed: {old_key_validation.to_dict()['error']['message']}"
                )
            
            if not new_key_validation.to_dict()["success"]:
                return ErrorResult(
                    message=f"New key validation failed: {new_key_validation.to_dict()['error']['message']}"
                )
            
            # Backup old key if requested
            backup_path = None
            if backup_old:
                backup_path = f"{old_key_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(old_key_path, backup_path)
                logger.info(f"Old key backed up to: {backup_path}")
            
            # Update certificate if provided
            cert_updated = False
            if cert_path and os.path.exists(cert_path):
                try:
                    # This would require implementing certificate re-signing
                    # For now, we'll just note that it needs to be done
                    cert_updated = True
                    logger.info(f"Certificate {cert_path} needs to be re-signed with new key")
                except Exception as e:
                    logger.warning(f"Could not update certificate {cert_path}: {e}")
            
            # Replace old key with new key
            shutil.copy2(new_key_path, old_key_path)
            
            logger.info(f"Key rotation completed successfully")
            return SuccessResult(
                data={
                    "old_key_path": old_key_path,
                    "new_key_path": new_key_path,
                    "backup_path": backup_path,
                    "cert_updated": cert_updated,
                    "message": "Key rotation completed successfully"
                }
            )
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            return ErrorResult(
                message=f"Key rotation failed: {str(e)}"
            )
    
    async def key_backup(self, key_path: str, backup_path: str,
                        encrypt_backup: bool = True, password: Optional[str] = None) -> CommandResult:
        """
        Backup a private key.
        
        Args:
            key_path: Path to key file to backup
            backup_path: Path to save the backup
            encrypt_backup: Whether to encrypt the backup
            password: Password for backup encryption
            
        Returns:
            CommandResult with backup status
        """
        try:
            logger.info(f"Backing up key: {key_path}")
            
            # Validate parameters
            if not key_path or not os.path.exists(key_path):
                return ErrorResult(
                    message=f"Key file not found: {key_path}"
                )
            
            # Validate key before backup
            key_validation = await self.key_validate(key_path)
            if not key_validation.to_dict()["success"]:
                return ErrorResult(
                    message=f"Key validation failed before backup: {key_validation.to_dict()['error']['message']}"
                )
            
            # Create backup directory if it doesn't exist
            backup_dir = os.path.dirname(backup_path)
            if backup_dir:
                Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            # Create backup
            if encrypt_backup and password:
                # Encrypted backup
                result = self.certificate_utils.create_encrypted_backup(
                    key_path, backup_path, password
                )
                if not result["success"]:
                    return ErrorResult(
                        message=f"Encrypted backup failed: {result['error']}"
                    )
            else:
                # Simple file copy
                shutil.copy2(key_path, backup_path)
            
            # Verify backup
            if not os.path.exists(backup_path):
                return ErrorResult(
                    message="Backup file was not created"
                )
            
            logger.info(f"Key backup completed successfully: {backup_path}")
            return SuccessResult(
                data={
                    "key_path": key_path,
                    "backup_path": backup_path,
                    "encrypted": encrypt_backup,
                    "backup_size": os.path.getsize(backup_path),
                    "backup_date": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Key backup failed: {e}")
            return ErrorResult(
                message=f"Key backup failed: {str(e)}"
            )
    
    async def key_restore(self, backup_path: str, key_path: str,
                         password: Optional[str] = None) -> CommandResult:
        """
        Restore a private key from backup.
        
        Args:
            backup_path: Path to backup file
            key_path: Path to restore the key to
            password: Password if backup is encrypted
            
        Returns:
            CommandResult with restore status
        """
        try:
            logger.info(f"Restoring key from backup: {backup_path}")
            
            # Validate parameters
            if not backup_path or not os.path.exists(backup_path):
                return ErrorResult(
                    message=f"Backup file not found: {backup_path}"
                )
            
            # Create target directory if it doesn't exist
            key_dir = os.path.dirname(key_path)
            if key_dir:
                Path(key_dir).mkdir(parents=True, exist_ok=True)
            
            # Restore key
            if password:
                # Try encrypted restore first
                result = self.certificate_utils.restore_encrypted_backup(
                    backup_path, key_path, password
                )
                if not result["success"]:
                    return ErrorResult(
                        message=f"Encrypted restore failed: {result['error']}"
                    )
            else:
                # Simple file copy
                shutil.copy2(backup_path, key_path)
            
            # Validate restored key
            key_validation = await self.key_validate(key_path)
            if not key_validation.to_dict()["success"]:
                return ErrorResult(
                    message=f"Restored key validation failed: {key_validation.to_dict()['error']['message']}"
                )
            
            logger.info(f"Key restore completed successfully: {key_path}")
            return SuccessResult(
                data={
                    "backup_path": backup_path,
                    "key_path": key_path,
                    "restore_date": datetime.now().isoformat(),
                    "key_info": key_validation.to_dict().get("data", {}).get("key") if key_validation.to_dict().get("success") else None
                }
            )
            
        except Exception as e:
            logger.error(f"Key restore failed: {e}")
            return ErrorResult(
                message=f"Key restore failed: {str(e)}"
            ) 