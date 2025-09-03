"""
Certificate Monitor Command

This module provides commands for certificate monitoring including expiry checks,
health monitoring, alert setup, and auto-renewal.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta

from .base import Command
from .result import CommandResult, SuccessResult, ErrorResult
from ..core.certificate_utils import CertificateUtils
from ..core.auth_validator import AuthValidator

logger = logging.getLogger(__name__)


class CertMonitorResult:
    """
    Result class for certificate monitoring operations.
    
    Contains monitoring information and operation status.
    """
    
    def __init__(self, cert_path: str, check_type: str, status: str,
                 expiry_date: Optional[str] = None, days_until_expiry: Optional[int] = None,
                 health_score: Optional[int] = None, alerts: Optional[List[str]] = None,
                 auto_renewal_status: Optional[str] = None, error: Optional[str] = None):
        """
        Initialize certificate monitor result.
        
        Args:
            cert_path: Path to certificate file
            check_type: Type of check performed (expiry, health, alert, auto_renewal)
            status: Overall status (healthy, warning, critical, error)
            expiry_date: Certificate expiry date
            days_until_expiry: Days until certificate expires
            health_score: Health score (0-100)
            alerts: List of alert messages
            auto_renewal_status: Auto-renewal status
            error: Error message if any
        """
        self.cert_path = cert_path
        self.check_type = check_type
        self.status = status
        self.expiry_date = expiry_date
        self.days_until_expiry = days_until_expiry
        self.health_score = health_score
        self.alerts = alerts or []
        self.auto_renewal_status = auto_renewal_status
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary representation
        """
        return {
            "cert_path": self.cert_path,
            "check_type": self.check_type,
            "status": self.status,
            "expiry_date": self.expiry_date,
            "days_until_expiry": self.days_until_expiry,
            "health_score": self.health_score,
            "alerts": self.alerts,
            "auto_renewal_status": self.auto_renewal_status,
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
                "cert_path": {"type": "string", "description": "Path to certificate file"},
                "check_type": {"type": "string", "enum": ["expiry", "health", "alert", "auto_renewal"], 
                              "description": "Type of check performed"},
                "status": {"type": "string", "enum": ["healthy", "warning", "critical", "error"], 
                          "description": "Overall status"},
                "expiry_date": {"type": "string", "description": "Certificate expiry date"},
                "days_until_expiry": {"type": "integer", "description": "Days until certificate expires"},
                "health_score": {"type": "integer", "minimum": 0, "maximum": 100, 
                               "description": "Health score (0-100)"},
                "alerts": {"type": "array", "items": {"type": "string"}, 
                          "description": "List of alert messages"},
                "auto_renewal_status": {"type": "string", "description": "Auto-renewal status"},
                "error": {"type": "string", "description": "Error message if any"}
            },
            "required": ["cert_path", "check_type", "status"]
        }


class CertMonitorCommand(Command):
    """
    Command for certificate monitoring.
    
    Provides methods for monitoring certificate expiry, health, alerts, and auto-renewal.
    """
    
    # Command metadata
    name = "cert_monitor"
    version = "1.0.0"
    descr = "Certificate expiry monitoring and health checks"
    category = "security"
    author = "MCP Proxy Adapter Team"
    email = "team@mcp-proxy-adapter.com"
    source_url = "https://github.com/mcp-proxy-adapter"
    result_class = CertMonitorResult
    
    def __init__(self):
        """Initialize certificate monitor command."""
        super().__init__()
        self.certificate_utils = CertificateUtils()
        self.auth_validator = AuthValidator()
    
    async def execute(self, **kwargs) -> CommandResult:
        """
        Execute certificate monitor command.
        
        Args:
            **kwargs: Command parameters including:
                - action: Action to perform (cert_expiry_check, cert_health_check, cert_alert_setup, cert_auto_renew)
                - cert_path: Certificate file path for individual checks
                - warning_days: Days before expiry to start warning
                - critical_days: Days before expiry for critical status
                - alert_config: Alert configuration for setup
                - auto_renew_config: Auto-renewal configuration
                
        Returns:
            CommandResult with monitoring operation status
        """
        action = kwargs.get("action", "cert_expiry_check")
        
        if action == "cert_expiry_check":
            cert_path = kwargs.get("cert_path")
            warning_days = kwargs.get("warning_days", 30)
            critical_days = kwargs.get("critical_days", 7)
            return await self.cert_expiry_check(cert_path, warning_days, critical_days)
        elif action == "cert_health_check":
            cert_path = kwargs.get("cert_path")
            return await self.cert_health_check(cert_path)
        elif action == "cert_alert_setup":
            cert_path = kwargs.get("cert_path")
            alert_config = kwargs.get("alert_config", {})
            return await self.cert_alert_setup(cert_path, alert_config)
        elif action == "cert_auto_renew":
            cert_path = kwargs.get("cert_path")
            auto_renew_config = kwargs.get("auto_renew_config", {})
            return await self.cert_auto_renew(cert_path, auto_renew_config)
        else:
            return ErrorResult(
                message=f"Unknown action: {action}. Supported actions: cert_expiry_check, cert_health_check, cert_alert_setup, cert_auto_renew"
            )
    
    async def cert_expiry_check(self, cert_path: str, warning_days: int = 30, critical_days: int = 7) -> CommandResult:
        """
        Check certificate expiry date.
        
        Args:
            cert_path: Path to certificate file
            warning_days: Days before expiry to start warning
            critical_days: Days before expiry for critical status
            
        Returns:
            CommandResult with expiry check results
        """
        try:
            logger.info(f"Performing certificate expiry check for {cert_path}")
            
            # Check if certificate file exists
            if not os.path.exists(cert_path):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_path}"
                )
            
            # Get certificate info
            cert_info = self.certificate_utils.get_certificate_info(cert_path)
            if not cert_info:
                return ErrorResult(
                    message="Could not read certificate information"
                )
            
            expiry_date = cert_info.get("expiry_date")
            if not expiry_date:
                return ErrorResult(
                    message="Could not determine certificate expiry date"
                )
            
            try:
                # Calculate days until expiry
                expiry_datetime = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                days_until_expiry = (expiry_datetime - datetime.now(expiry_datetime.tzinfo)).days
            except ValueError:
                return ErrorResult(
                    message="Invalid expiry date format"
                )
            
            # Determine status
            is_expired = days_until_expiry < 0
            if is_expired:
                health_status = "expired"
            elif days_until_expiry <= critical_days:
                health_status = "critical"
            elif days_until_expiry <= warning_days:
                health_status = "warning"
            else:
                health_status = "healthy"
            
            logger.info(f"Certificate expiry check completed: {health_status} ({days_until_expiry} days)")
            
            return SuccessResult(
                data={
                    "monitor_result": {
                        "is_expired": is_expired,
                        "health_status": health_status,
                        "days_until_expiry": days_until_expiry,
                        "expiry_date": expiry_date,
                        "warning_days": warning_days,
                        "critical_days": critical_days
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Certificate expiry check failed: {e}")
            return ErrorResult(
                message=f"Certificate expiry check failed: {str(e)}"
            )
    
    async def cert_health_check(self, cert_path: str) -> CommandResult:
        """
        Perform comprehensive health check on certificate.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            CommandResult with health check results
        """
        try:
            logger.info(f"Performing certificate health check for {cert_path}")
            
            # Check if certificate file exists
            if not os.path.exists(cert_path):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_path}"
                )
            
            # Get certificate info
            cert_info = self.certificate_utils.get_certificate_info(cert_path)
            if not cert_info:
                return ErrorResult(
                    message="Could not read certificate information"
                )
            
            # Validate certificate
            validation = self.auth_validator.validate_certificate(cert_path)
            
            # Calculate health score
            health_score = 100
            alerts = []
            
            # Check if certificate is valid
            if not validation.is_valid:
                health_score -= 50
                alerts.append(f"Certificate validation failed: {validation.error_message}")
            
            # Check expiry
            expiry_date = cert_info.get("expiry_date")
            if expiry_date:
                try:
                    expiry_datetime = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                    days_until_expiry = (expiry_datetime - datetime.now(expiry_datetime.tzinfo)).days
                    
                    if days_until_expiry < 0:
                        health_score -= 30
                        alerts.append("Certificate has expired")
                    elif days_until_expiry <= 7:
                        health_score -= 20
                        alerts.append(f"Certificate expires in {days_until_expiry} days")
                    elif days_until_expiry <= 30:
                        health_score -= 10
                        alerts.append(f"Certificate expires in {days_until_expiry} days")
                except ValueError:
                    health_score -= 10
                    alerts.append("Invalid expiry date format")
            
            # Check key strength
            key_size = cert_info.get("key_size", 0)
            if key_size < 2048:
                health_score -= 15
                alerts.append(f"Key size {key_size} bits is below recommended 2048 bits")
            
            # Determine overall status
            if health_score >= 80:
                overall_status = "healthy"
            elif health_score >= 50:
                overall_status = "warning"
            else:
                overall_status = "critical"
            
            logger.info(f"Certificate health check completed: {overall_status} (score: {health_score})")
            
            return SuccessResult(
                data={
                    "monitor_result": {
                        "health_score": health_score,
                        "alerts": alerts,
                        "expiry_date": expiry_date
                    },
                    "health_checks": {
                        "validation": {
                            "passed": validation.is_valid
                        }
                    },
                    "overall_status": overall_status
                }
            )
            
        except Exception as e:
            logger.error(f"Certificate health check failed: {e}")
            return ErrorResult(
                message=f"Certificate health check failed: {str(e)}"
            )
    
    async def cert_alert_setup(self, cert_path: str, alert_config: Dict[str, Any]) -> CommandResult:
        """
        Set up certificate monitoring alerts.
        
        Args:
            cert_path: Path to certificate file
            alert_config: Alert configuration dictionary
            
        Returns:
            CommandResult with alert setup status
        """
        try:
            logger.info(f"Setting up certificate monitoring alerts for {cert_path}")
            
            # Check if certificate file exists
            if not os.path.exists(cert_path):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_path}"
                )
            
            # Validate alert configuration
            if not isinstance(alert_config, dict):
                return ErrorResult(
                    message="Alert configuration must be a dictionary"
                )
            
            # Check if alerts are disabled
            if not alert_config.get("enabled", True):
                return SuccessResult(
                    data={
                        "monitor_result": {
                            "alerts_enabled": False
                        },
                        "message": "Alerts disabled"
                    }
                )
            
            # Validate required fields
            required_fields = ["warning_days", "critical_days"]
            for field in required_fields:
                if field not in alert_config:
                    return ErrorResult(
                        message=f"Missing required field in alert config: {field}"
                    )
            
            if alert_config["warning_days"] <= 0 or alert_config["critical_days"] <= 0:
                return ErrorResult(
                    message="Warning and critical days must be positive"
                )
            
            if alert_config["warning_days"] <= alert_config["critical_days"]:
                return ErrorResult(
                    message="Warning days must be greater than critical days"
                )
            
            # Check notification channels
            notification_channels = alert_config.get("notification_channels", [])
            if not notification_channels:
                return ErrorResult(
                    message="At least one notification channel must be specified"
                )
            
            # Test alert configuration
            test_result = await self._test_alert_config(alert_config)
            if not test_result["success"]:
                return ErrorResult(
                    message=f"Alert configuration test failed: {test_result['error']}"
                )
            
            # Save alert configuration
            config_path = "/tmp/cert_alert_config.json"
            with open(config_path, 'w') as f:
                json.dump(alert_config, f, indent=2)
            
            logger.info(f"Alert configuration saved to {config_path}")
            
            return SuccessResult(
                data={
                    "monitor_result": {
                        "alerts_enabled": True
                    },
                    "alert_config": alert_config,
                    "config_path": config_path,
                    "setup_date": datetime.now().isoformat(),
                    "message": "Alerts configured successfully"
                }
            )
            
        except Exception as e:
            logger.error(f"Alert setup failed: {e}")
            return ErrorResult(
                message=f"Alert setup failed: {str(e)}"
            )
    
    async def cert_auto_renew(self, cert_path: str, auto_renew_config: Dict[str, Any]) -> CommandResult:
        """
        Set up certificate auto-renewal.
        
        Args:
            cert_path: Path to certificate file
            auto_renew_config: Auto-renewal configuration dictionary
            
        Returns:
            CommandResult with auto-renewal setup status
        """
        try:
            logger.info(f"Setting up certificate auto-renewal for {cert_path}")
            
            # Check if certificate file exists
            if not os.path.exists(cert_path):
                return ErrorResult(
                    message=f"Certificate file not found: {cert_path}"
                )
            
            # Validate auto-renewal configuration
            if not isinstance(auto_renew_config, dict):
                return ErrorResult(
                    message="Auto-renewal configuration must be a dictionary"
                )
            
            # Check if auto-renewal is disabled
            if not auto_renew_config.get("enabled", True):
                return SuccessResult(
                    data={
                        "monitor_result": {
                            "auto_renewal_enabled": False
                        },
                        "message": "Auto-renewal disabled"
                    }
                )
            
            # Validate required fields
            required_fields = ["renew_before_days", "ca_cert_path", "ca_key_path"]
            for field in required_fields:
                if field not in auto_renew_config:
                    return ErrorResult(
                        message=f"Missing required field in auto-renewal config: {field}"
                    )
            
            if auto_renew_config["renew_before_days"] <= 0:
                return ErrorResult(
                    message="Renew before days must be positive"
                )
            
            # Check CA files
            ca_cert_path = auto_renew_config["ca_cert_path"]
            ca_key_path = auto_renew_config["ca_key_path"]
            
            if not os.path.exists(ca_cert_path):
                return ErrorResult(
                    message=f"CA certificate not found: {ca_cert_path}"
                )
            
            if not os.path.exists(ca_key_path):
                return ErrorResult(
                    message=f"CA private key not found: {ca_key_path}"
                )
            
            # Check output directory
            output_dir = auto_renew_config.get("output_dir")
            if not output_dir:
                return ErrorResult(
                    message="Output directory must be specified"
                )
            
            # Test renewal configuration
            test_result = await self._test_renewal_config(cert_path, auto_renew_config)
            if not test_result["success"]:
                return ErrorResult(
                    message=f"Renewal configuration test failed: {test_result['error']}"
                )
            
            # Save auto-renewal configuration
            config_path = "/tmp/cert_auto_renew_config.json"
            with open(config_path, 'w') as f:
                json.dump(auto_renew_config, f, indent=2)
            
            logger.info(f"Auto-renewal configuration saved to {config_path}")
            
            return SuccessResult(
                data={
                    "monitor_result": {
                        "auto_renewal_enabled": True
                    },
                    "auto_renew_config": auto_renew_config,
                    "config_path": config_path,
                    "setup_date": datetime.now().isoformat(),
                    "message": "Auto-renewal configured successfully"
                }
            )
            
        except Exception as e:
            logger.error(f"Auto-renewal setup failed: {e}")
            return ErrorResult(
                message=f"Auto-renewal setup failed: {str(e)}"
            )
    
    def _find_certificates(self, directory: str) -> List[str]:
        """
        Find all certificate files in a directory.
        
        Args:
            directory: Directory to scan
            
        Returns:
            List of certificate file paths
        """
        certificates = []
        cert_extensions = ['.crt', '.pem', '.cer', '.der']
        
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in cert_extensions:
                certificates.append(str(file_path))
        
        return certificates
    
    async def _test_alert_config(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test alert configuration.
        
        Args:
            alert_config: Alert configuration to test
            
        Returns:
            Test result dictionary
        """
        try:
            # Test email configuration if present
            if "email_recipients" in alert_config:
                recipients = alert_config["email_recipients"]
                if not isinstance(recipients, list) or not recipients:
                    return {"success": False, "error": "Invalid email recipients"}
            
            # Test webhook configuration if present
            if "webhook_url" in alert_config:
                webhook_url = alert_config["webhook_url"]
                if not isinstance(webhook_url, str) or not webhook_url:
                    return {"success": False, "error": "Invalid webhook URL"}
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_renewal_config(self, cert_path: str, renewal_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test renewal configuration.
        
        Args:
            cert_path: Path to certificate file
            renewal_config: Renewal configuration to test
            
        Returns:
            Test result dictionary
        """
        try:
            # Get certificate info
            cert_info = self.certificate_utils.get_certificate_info(cert_path)
            if not cert_info:
                return {"success": False, "error": "Could not read certificate information"}
            
            # Check CA certificate
            ca_cert_path = renewal_config.get("ca_cert_path")
            if not ca_cert_path or not os.path.exists(ca_cert_path):
                return {"success": False, "error": "CA certificate not found"}
            
            # Check CA key
            ca_key_path = renewal_config.get("ca_key_path")
            if not ca_key_path or not os.path.exists(ca_key_path):
                return {"success": False, "error": "CA private key not found"}
            
            # Check output directory
            output_dir = renewal_config.get("output_dir")
            if not output_dir or not os.path.exists(output_dir):
                return {"success": False, "error": "Output directory not found"}
            
            return {"success": True}
            
        except Exception as e:
            return {"success": False, "error": str(e)} 