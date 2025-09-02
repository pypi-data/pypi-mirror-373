"""
Module with utility functions for the microservice.
"""

import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from mcp_proxy_adapter.core.logging import logger


def generate_id() -> str:
    """
    Generates a unique identifier.

    Returns:
        String with unique identifier.
    """
    return str(uuid.uuid4())


def get_timestamp() -> int:
    """
    Returns current timestamp in milliseconds.

    Returns:
        Integer - timestamp in milliseconds.
    """
    return int(time.time() * 1000)


def format_datetime(dt: Optional[datetime] = None, format_str: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> str:
    """
    Formats date and time as string.

    Args:
        dt: Datetime object to format. If None, current time is used.
        format_str: Format string for output.

    Returns:
        Formatted date/time string.
    """
    dt = dt or datetime.now(timezone.utc)
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> datetime:
    """
    Parses date/time string into datetime object.

    Args:
        dt_str: Date/time string.
        format_str: Date/time string format.

    Returns:
        Datetime object.
    """
    return datetime.strptime(dt_str, format_str)


def safe_json_loads(s: str, default: Any = None) -> Any:
    """
    Safe JSON string loading.

    Args:
        s: JSON string to load.
        default: Default value on parsing error.

    Returns:
        Loaded object or default value on error.
    """
    try:
        return json.loads(s)
    except Exception as e:
        logger.error(f"Error parsing JSON: {e}")
        return default


def safe_json_dumps(obj: Any, default: str = "{}", indent: Optional[int] = None) -> str:
    """
    Safe object conversion to JSON string.

    Args:
        obj: Object to convert.
        default: Default string on serialization error.
        indent: Indentation for JSON formatting.

    Returns:
        JSON string or default string on error.
    """
    try:
        return json.dumps(obj, ensure_ascii=False, indent=indent)
    except Exception as e:
        logger.error(f"Error serializing to JSON: {e}")
        return default


def calculate_hash(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """
    Calculates hash for data.

    Args:
        data: Data to hash (string or bytes).
        algorithm: Hashing algorithm (md5, sha1, sha256, etc.).

    Returns:
        String with hash in hexadecimal format.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    return hash_obj.hexdigest()


def ensure_directory(path: str) -> bool:
    """
    Checks directory existence and creates it if necessary.

    Args:
        path: Path to directory.

    Returns:
        True if directory exists or was successfully created, otherwise False.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False
