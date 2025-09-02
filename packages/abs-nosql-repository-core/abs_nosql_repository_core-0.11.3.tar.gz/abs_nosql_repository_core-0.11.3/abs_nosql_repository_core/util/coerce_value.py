from datetime import datetime
from functools import lru_cache
from typing import Any, Union, Dict, List
from bson import ObjectId
# Cache for datetime format parsing
@lru_cache(maxsize=128)
def parse_datetime(value: str) -> Union[datetime, str]:
    """
    Parse datetime string with caching for better performance.
    Supports multiple ISO 8601 formats.
    """
    formats = [
        # ISO 8601 formats with time
        "%Y-%m-%dT%H:%M:%S",  # 2025-05-10T14:00:00
        "%Y-%m-%dT%H:%M:%SZ",  # 2025-05-10T14:00:00Z
        "%Y-%m-%dT%H:%M:%S.%f",  # 2025-05-10T14:00:00.123456
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2025-05-10T14:00:00.123456Z
        
        # ISO 8601 formats with timezone offset
        "%Y-%m-%dT%H:%M:%S%z",  # 2025-05-10T14:00:00+0530
        "%Y-%m-%dT%H:%M:%S.%f%z",  # 2025-05-10T14:00:00.123456+05:30
        
        # Date only formats
        "%Y-%m-%d",  # 2025-05-10
        "%Y/%m/%d",  # 2025/05/10
        "%m-%d-%Y",  # 05-10-2025
        "%m/%d/%Y",  # 05/10/2025
        
        # Time only formats
        "%H:%M:%S",  # 14:00:00
        
        # Common date and time formats without T separator
        "%Y-%m-%d %H:%M:%S",  # 2025-05-10 14:00:00
        "%Y-%m-%d %H:%M:%S.%f",  # 2025-05-10 14:00:00.123456
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return value

# Cache for boolean string values
BOOLEAN_MAP = {
    "true": True, 
    "false": False
}

def coerce_value(value: Any) -> Any:
    """
    Coerce a value to its appropriate Python type.
    Handles nested structures (lists and dicts) recursively.
    Optimized for common cases and includes caching for better performance.
    """
    # Fast path for non-string types
    if not isinstance(value, str):
        if isinstance(value, list):
            return [coerce_value(item) for item in value]
        if isinstance(value, dict):
            return {k: coerce_value(v) for k, v in value.items()}
        return value

    # Fast path for empty string
    if not value:
        return value

    # Check boolean/null values first (most common case)
    lowered = value.lower()
    if lowered in BOOLEAN_MAP:
        return BOOLEAN_MAP[lowered]
    
    try:
        if ObjectId.is_valid(value):
            return ObjectId(value)
    except Exception as e:
        pass
    
    # Check for datetime (least common case)
    return parse_datetime(value)
