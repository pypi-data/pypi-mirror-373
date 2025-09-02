"""
Serialization utilities - Functions for converting data types to serializable formats
"""

from typing import Any, Union, Dict, List
from datetime import datetime


def datetime_serializer(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Utility to serialize datetime objects to ISO format for cache storage.
    Recursively processes dictionaries and lists to convert all datetime objects.
    
    Args:
        data: Data structure that may contain datetime objects
        
    Returns:
        Data structure with datetime objects converted to ISO format strings
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                datetime_serializer(value)
    elif isinstance(data, list):
        for index, value in enumerate(data):
            if isinstance(value, datetime):
                data[index] = value.isoformat()
            elif isinstance(value, (dict, list)):
                datetime_serializer(value)
    return data 