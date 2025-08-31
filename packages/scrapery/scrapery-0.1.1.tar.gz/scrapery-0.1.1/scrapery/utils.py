# utils.py

import re
import os
import chardet
from typing import Any, Optional, Union
from .exceptions import FileError, EncodingError, ValidationError

# -------------------------------
# LXML Element Check
# -------------------------------

from lxml.etree import _Element as LxmlElement

def is_element(element: Any) -> bool:
    """Check if an object is a valid lxml element."""
    return isinstance(element, LxmlElement)

def validate_element(element: Any, raise_error: bool = True) -> bool:
    """Validate if an object is a valid lxml element."""
    if is_element(element):
        return True
    if raise_error:
        raise ValidationError("Invalid element provided")
    return False

# -------------------------------
# Safe Text Extraction
# -------------------------------

def safe_get_selector_text(element: Any, default: str = "", **kwargs) -> str:
    """Safely extract text from an element with fallback."""
    if is_element(element):
        from .html import get_selector_text
        try:
            return get_selector_text(element, **kwargs)
        except Exception:
            return default
    return default

# -------------------------------
# Encoding Detection
# -------------------------------

def detect_encoding(content: Union[str, bytes]) -> str:
    """Detect encoding of content efficiently."""
    if isinstance(content, str):
        return 'utf-8'
    result = chardet.detect(content)
    encoding = result.get('encoding') or 'utf-8'
    try:
        content.decode(encoding)
        return encoding
    except (UnicodeDecodeError, LookupError):
        return 'utf-8'

# -------------------------------
# HTML Normalization
# -------------------------------

_normalize_comments_re = re.compile(r'<!--.*?-->', re.DOTALL)

def normalize_html(html_content: str) -> str:
    """Normalize HTML for faster parsing."""
    html_content = re.sub(r'>\s+<', '><', html_content)
    html_content = html_content.replace('&nbsp;', ' ')
    html_content = _normalize_comments_re.sub('', html_content)
    return html_content

# -------------------------------
# File Reading
# -------------------------------

def read_file(file_path: str, encoding: Optional[str] = None) -> str:
    """Read file content with efficient encoding detection."""
    if not os.path.isfile(file_path):
        raise FileError(f"File not found or not a file: {file_path}")
    
    with open(file_path, 'rb') as f:
        content = f.read()
    
    if not encoding:
        encoding = detect_encoding(content)
    
    try:
        return content.decode(encoding)
    except UnicodeDecodeError:
        # Fallback to utf-8 with replacement
        try:
            return content.decode('utf-8', errors='replace')
        except Exception:
            raise EncodingError(f"Failed to decode file: {file_path}")

# -------------------------------
# Input Validation
# -------------------------------

def validate_input(data: Any, data_type: Optional[type] = None) -> None:
    """Validate input data with type checking."""
    if data is None:
        raise ValidationError("Input data cannot be None")
    if isinstance(data, str) and not data.strip():
        raise ValidationError("Input data cannot be empty string")
    if data_type and not isinstance(data, data_type):
        raise ValidationError(f"Input data must be of type {data_type.__name__}")

# -------------------------------
# Utility Functions
# -------------------------------

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to integer with default fallback."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None

# 👇 Explicitly define the public API for utils.py
__all__ = [
    "is_element",
    "validate_element",
    "safe_get_selector_text",
    "detect_encoding",
    "normalize_html",
    "read_file",
    "validate_input",
    "safe_int",
    "extract_domain",
]