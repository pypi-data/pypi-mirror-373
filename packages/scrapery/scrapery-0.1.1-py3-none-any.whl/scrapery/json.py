# json.py

import os
from typing import Dict, List, Optional, Any, Union
import ujson as json
from .exceptions import ParserError, FileError
from .utils import validate_input, read_file

# -------------------------------
# JSON Parsing
# -------------------------------

def parse_json(
    json_content: str,
    precise_float: bool = False,
    escape_forward_slashes: bool = False
) -> Union[Dict, List]:
    """
    Parse JSON content or file path with ujson for maximum performance.
    
    Args:
        json_content: JSON string or file path
        precise_float: Use precise float parsing
        escape_forward_slashes: Escape forward slashes
    
    Returns:
        Parsed JSON data (dict or list)
    
    Raises:
        ParserError: If JSON parsing fails
    """
    # Handle file path automatically
    if isinstance(json_content, str) and os.path.exists(json_content) and os.path.isfile(json_content):
        try:
            json_content = read_file(json_content)
        except FileError:
            raise
        except Exception as e:
            raise ParserError(f"Failed to read JSON file {json_content}: {str(e)}")

    validate_input(json_content, str)

    try:
        return json.loads(json_content, precise_float=precise_float, escape_forward_slashes=escape_forward_slashes)
    except ValueError as e:
        raise ParserError(f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise ParserError(f"Unexpected error during JSON parsing: {str(e)}")


# -------------------------------
# JSON Search
# -------------------------------

def json_search(data: Any, query: str) -> Any:
    """
    Search JSON data using JMESPath query.
    
    Args:
        data: JSON data to search
        query: JMESPath query
    
    Returns:
        Query results
    
    Raises:
        ParserError: If query fails
    """
    validate_input(data)
    validate_input(query, str)

    try:
        import jmespath
        result = jmespath.search(query, data)
        if result is None:
            raise ParserError(f"JMESPath query returned no results: {query}")
        return result
    except ImportError:
        raise ImportError("JMESPath is required for JSON queries. Install with 'pip install jmespath'")
    except Exception as e:
        raise ParserError(f"JMESPath query error for '{query}': {str(e)}")


# -------------------------------
# JSON Value Get
# -------------------------------

def json_get_value(
    data: Any,
    path: str,
    default: Any = None,
    separator: str = "."
) -> Any:
    """
    Get value from JSON using path notation (dot-separated).
    
    Args:
        data: JSON data
        path: Dot-separated path (e.g., 'user.address.city')
        default: Default value if path not found
        separator: Path separator
    
    Returns:
        Value at path or default
    """
    validate_input(data)
    validate_input(path, str)

    try:
        parts = path.split(separator)
        current = data
        for part in parts:
            if isinstance(current, list):
                try:
                    index = int(part)
                    current = current[index]
                except (ValueError, IndexError):
                    return default
            elif isinstance(current, dict):
                current = current.get(part, default)
                if current is default:
                    return default
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError):
        return default


# -------------------------------
# JSON Extract Values
# -------------------------------

def json_extract_values(data: Any, key_pattern: str, case_sensitive: bool = True) -> List[Any]:
    """
    Extract all values matching a key pattern.
    Iterative for large JSON.
    """
    results = []
    from collections import deque
    stack = deque([data])

    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for k, v in current.items():
                match = key_pattern in k if case_sensitive else key_pattern.lower() in k.lower()
                if match:
                    results.append(v)
                stack.append(v)
        elif isinstance(current, list):
            stack.extend(current)
    return results


# -------------------------------
# JSON Validation
# -------------------------------

def json_validate(data: Any, schema: Optional[Any] = None) -> bool:
    """
    Validate JSON against optional schema (dict type).
    Simple validation for key existence and type check.
    """
    try:
        if schema and isinstance(schema, dict):
            for key, value_type in schema.items():
                if key not in data or not isinstance(data[key], value_type):
                    return False
        return True
    except Exception:
        return False


# -------------------------------
# JSON Flatten
# -------------------------------

def json_flatten(data: Any, separator: str = ".", prefix: str = "") -> Dict[str, Any]:
    """
    Flatten nested JSON structure into a dictionary with dotted keys.
    Iterative version for performance.
    """
    from collections import deque

    items: Dict[str, Any] = {}
    stack = deque([(prefix, data)])

    while stack:
        parent_key, obj = stack.pop()
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{parent_key}{separator}{k}" if parent_key else k
                stack.append((new_key, v))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                new_key = f"{parent_key}{separator}{i}" if parent_key else str(i)
                stack.append((new_key, v))
        else:
            items[parent_key] = obj

    return items


__all__ = [
    "parse_json",
    "json_search",
    "json_get_value",
    "json_extract_values",
    "json_validate",
    "json_flatten",
]        