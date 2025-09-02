from typing import Any
from datetime import datetime
from decimal import Decimal
from bson import ObjectId

def convert_to_text(data: Any) -> str:
    if data is None:
        return ""

    if isinstance(data, (int, float, bool, datetime, Decimal, ObjectId)):
        return str(data)
    
    if isinstance(data, (list, tuple, set)):
        return ", ".join(convert_to_text(item) for item in data)
    
    if isinstance(data, dict):
        return ", ".join(f"{key}: {convert_to_text(value)}" for key, value in data.items())
    
    if isinstance(data, str):
        return data
    
    return str(data)