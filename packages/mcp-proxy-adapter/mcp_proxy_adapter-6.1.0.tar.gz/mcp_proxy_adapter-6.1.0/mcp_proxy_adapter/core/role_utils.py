"""
Role Utilities

This module provides utilities for working with roles extracted from certificates.
Includes functions for role extraction, comparison, validation, and normalization.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
from typing import List, Optional, Set
from cryptography import x509


class RoleUtils:
    """
    Utilities for working with roles from certificates.
    
    Provides methods for extracting, comparing, validating, and normalizing roles.
    """
    
    # Custom OID for roles in certificates
    ROLE_EXTENSION_OID = "1.3.6.1.4.1.99999.1"
    
    @staticmethod
    def extract_roles_from_certificate(cert_path: str) -> List[str]:
        """
        Extract roles from certificate file.
        
        Args:
            cert_path: Path to certificate file
            
        Returns:
            List of roles extracted from certificate
        """
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data)
            
            # Extract roles from custom extension
            for extension in cert.extensions:
                if extension.oid.dotted_string == RoleUtils.ROLE_EXTENSION_OID:
                    roles_data = extension.value.value.decode('utf-8')
                    return [role.strip() for role in roles_data.split(',') if role.strip()]
            
            return []
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to extract roles from certificate {cert_path}: {e}")
            return []
    
    @staticmethod
    def extract_roles_from_certificate_object(cert: x509.Certificate) -> List[str]:
        """
        Extract roles from certificate object.
        
        Args:
            cert: Certificate object
            
        Returns:
            List of roles extracted from certificate
        """
        try:
            # Extract roles from custom extension
            for extension in cert.extensions:
                if extension.oid.dotted_string == RoleUtils.ROLE_EXTENSION_OID:
                    roles_data = extension.value.value.decode('utf-8')
                    return [role.strip() for role in roles_data.split(',') if role.strip()]
            
            return []
            
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to extract roles from certificate object: {e}")
            return []
    
    @staticmethod
    def compare_roles(role1: str, role2: str) -> bool:
        """
        Compare two roles (case-insensitive).
        
        Args:
            role1: First role to compare
            role2: Second role to compare
            
        Returns:
            True if roles are equal (case-insensitive), False otherwise
        """
        if not role1 or not role2:
            return False
        
        return role1.lower().strip() == role2.lower().strip()
    
    @staticmethod
    def compare_role_lists(roles1: List[str], roles2: List[str]) -> bool:
        """
        Compare two lists of roles (case-insensitive).
        
        Args:
            roles1: First list of roles
            roles2: Second list of roles
            
        Returns:
            True if role lists are equal (case-insensitive), False otherwise
        """
        if not roles1 and not roles2:
            return True
        
        if not roles1 or not roles2:
            return False
        
        # Normalize and sort both lists
        normalized_roles1 = sorted([role.lower().strip() for role in roles1 if role.strip()])
        normalized_roles2 = sorted([role.lower().strip() for role in roles2 if role.strip()])
        
        return normalized_roles1 == normalized_roles2
    
    @staticmethod
    def validate_roles(roles: List[str]) -> bool:
        """
        Validate list of roles.
        
        Args:
            roles: List of roles to validate
            
        Returns:
            True if roles are valid, False otherwise
        """
        if not isinstance(roles, list):
            return False
        
        for role in roles:
            if not RoleUtils.validate_single_role(role):
                return False
        
        return True
    
    @staticmethod
    def validate_single_role(role: str) -> bool:
        """
        Validate a single role.
        
        Args:
            role: Role string to validate
            
        Returns:
            True if role is valid, False otherwise
        """
        if not isinstance(role, str):
            return False
        
        # Check if role is not empty after trimming
        if not role.strip():
            return False
        
        # Check for valid characters (alphanumeric, hyphens, underscores)
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        role_chars = set(role.lower())
        
        if not role_chars.issubset(valid_chars):
            return False
        
        # Check length (1-50 characters)
        if len(role) < 1 or len(role) > 50:
            return False
        
        return True
    
    @staticmethod
    def normalize_role(role: str) -> str:
        """
        Normalize role string.
        
        Args:
            role: Role string to normalize
            
        Returns:
            Normalized role string
        """
        if not role:
            return ""
        
        # Convert to lowercase and trim whitespace
        normalized = role.lower().strip()
        
        # Replace multiple spaces with single space
        normalized = ' '.join(normalized.split())
        
        # Replace spaces with hyphens
        normalized = normalized.replace(' ', '-')
        
        return normalized
    
    @staticmethod
    def normalize_roles(roles: List[str]) -> List[str]:
        """
        Normalize list of roles.
        
        Args:
            roles: List of roles to normalize
            
        Returns:
            List of normalized roles
        """
        if not roles:
            return []
        
        normalized = []
        for role in roles:
            normalized_role = RoleUtils.normalize_role(role)
            if normalized_role and normalized_role not in normalized:
                normalized.append(normalized_role)
        
        return normalized
    
    @staticmethod
    def has_role(user_roles: List[str], required_role: str) -> bool:
        """
        Check if user has required role.
        
        Args:
            user_roles: List of user roles
            required_role: Required role to check
            
        Returns:
            True if user has required role, False otherwise
        """
        if not user_roles or not required_role:
            return False
        
        normalized_required = RoleUtils.normalize_role(required_role)
        normalized_user_roles = RoleUtils.normalize_roles(user_roles)
        
        return normalized_required in normalized_user_roles
    
    @staticmethod
    def has_any_role(user_roles: List[str], required_roles: List[str]) -> bool:
        """
        Check if user has any of the required roles.
        
        Args:
            user_roles: List of user roles
            required_roles: List of required roles to check
            
        Returns:
            True if user has any required role, False otherwise
        """
        if not user_roles or not required_roles:
            return False
        
        normalized_user_roles = RoleUtils.normalize_roles(user_roles)
        normalized_required_roles = RoleUtils.normalize_roles(required_roles)
        
        return any(role in normalized_user_roles for role in normalized_required_roles)
    
    @staticmethod
    def has_all_roles(user_roles: List[str], required_roles: List[str]) -> bool:
        """
        Check if user has all required roles.
        
        Args:
            user_roles: List of user roles
            required_roles: List of required roles to check
            
        Returns:
            True if user has all required roles, False otherwise
        """
        if not user_roles or not required_roles:
            return False
        
        normalized_user_roles = RoleUtils.normalize_roles(user_roles)
        normalized_required_roles = RoleUtils.normalize_roles(required_roles)
        
        return all(role in normalized_user_roles for role in normalized_required_roles)
    
    @staticmethod
    def get_common_roles(roles1: List[str], roles2: List[str]) -> List[str]:
        """
        Get common roles between two role lists.
        
        Args:
            roles1: First list of roles
            roles2: Second list of roles
            
        Returns:
            List of common roles
        """
        if not roles1 or not roles2:
            return []
        
        normalized_roles1 = set(RoleUtils.normalize_roles(roles1))
        normalized_roles2 = set(RoleUtils.normalize_roles(roles2))
        
        return list(normalized_roles1.intersection(normalized_roles2))
    
    @staticmethod
    def merge_roles(roles1: List[str], roles2: List[str]) -> List[str]:
        """
        Merge two role lists (remove duplicates).
        
        Args:
            roles1: First list of roles
            roles2: Second list of roles
            
        Returns:
            Merged list of roles without duplicates
        """
        all_roles = (roles1 or []) + (roles2 or [])
        return RoleUtils.normalize_roles(all_roles)
    
    @staticmethod
    def remove_roles(roles: List[str], roles_to_remove: List[str]) -> List[str]:
        """
        Remove specified roles from role list.
        
        Args:
            roles: List of roles
            roles_to_remove: List of roles to remove
            
        Returns:
            List of roles with specified roles removed
        """
        if not roles:
            return []
        
        if not roles_to_remove:
            return roles.copy()
        
        normalized_roles = RoleUtils.normalize_roles(roles)
        normalized_to_remove = set(RoleUtils.normalize_roles(roles_to_remove))
        
        return [role for role in normalized_roles if role not in normalized_to_remove]
    
    @staticmethod
    def is_admin_role(role: str) -> bool:
        """
        Check if role is an admin role.
        
        Args:
            role: Role to check
            
        Returns:
            True if role is admin, False otherwise
        """
        if not role:
            return False
        
        admin_roles = {'admin', 'administrator', 'root', 'superuser', 'super-admin'}
        normalized_role = RoleUtils.normalize_role(role)
        
        return normalized_role in admin_roles
    
    @staticmethod
    def is_system_role(role: str) -> bool:
        """
        Check if role is a system role.
        
        Args:
            role: Role to check
            
        Returns:
            True if role is system role, False otherwise
        """
        if not role:
            return False
        
        system_roles = {'system', 'service', 'daemon', 'internal', 'system-user'}
        normalized_role = RoleUtils.normalize_role(role)
        
        return normalized_role in system_roles
    
    @staticmethod
    def get_role_hierarchy(role: str) -> List[str]:
        """
        Get role hierarchy (parent roles).
        
        Args:
            role: Role to get hierarchy for
            
        Returns:
            List of parent roles in hierarchy
        """
        if not role:
            return []
        
        normalized_role = RoleUtils.normalize_role(role)
        
        # Define role hierarchy
        hierarchy = {
            'super-admin': ['admin', 'user'],
            'admin': ['user'],
            'moderator': ['user'],
            'user': [],
            'guest': []
        }
        
        return hierarchy.get(normalized_role, [])
    
    @staticmethod
    def get_role_permissions(role: str) -> List[str]:
        """
        Get permissions for a role.
        
        Args:
            role: Role to get permissions for
            
        Returns:
            List of permissions for the role
        """
        if not role:
            return []
        
        normalized_role = RoleUtils.normalize_role(role)
        
        # Define role permissions
        permissions = {
            'super-admin': ['read', 'write', 'delete', 'admin', 'system'],
            'admin': ['read', 'write', 'delete', 'admin'],
            'moderator': ['read', 'write', 'moderate'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
        
        return permissions.get(normalized_role, []) 