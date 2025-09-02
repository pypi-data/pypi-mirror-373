"""
Data manipulation utilities - Functions for normalizing and merging data structures
"""

from typing import Dict, Any, Union, List


def normalize(value: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
    """
    Utility to normalize a dictionary for consistent cache key generation.
    Recursively sorts dictionary keys and normalizes nested structures.
    
    Args:
        value: The value to normalize (dict, list, or primitive)
        
    Returns:
        Normalized value with sorted keys for dictionaries
    """
    if isinstance(value, dict):
        return {k: normalize(value[k]) for k in sorted(value)}
    elif isinstance(value, list):
        return [normalize(v) for v in value]
    else:
        return value


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, handling nested structures and arrays.
    
    Args:
        *dicts: Variable number of dictionaries to merge
        
    Returns:
        Merged dictionary with nested structures properly combined
    """
    def merge(a: Dict[str, Any], b: Dict[str, Any]) -> None:
        """Internal merge function that modifies dictionary a in place"""
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    merge(a[key], b[key])
                elif isinstance(a[key], list) and isinstance(b[key], list):
                    a[key].extend(b[key])
                elif isinstance(a[key], list):
                    a[key].append(b[key])
                elif isinstance(b[key], list):
                    b[key].insert(0, a[key])
                    a[key] = b[key]
                else:
                    a[key] = [a[key], b[key]]
            else:
                a[key] = b[key]

    result = {}
    for d in dicts:
        merge(result, d)
    return result 