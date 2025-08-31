# html.py

import os
import re
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any, Union
from lxml import html, etree
from .utils import validate_input, validate_element, read_file, safe_get_selector_text, normalize_html
from .exceptions import ParserError, SelectorError, FileError, ValidationError


def parse_html(
    html_content: str,
    encoding: Optional[str] = None,
    normalize: bool = True,
    recover: bool = True,
    remove_comments: bool = True,
    remove_scripts: bool = False,
    remove_styles: bool = False,
    remove_noscript: bool = False,
    **parser_kwargs
) -> html.HtmlElement:
    """
    High-performance HTML parsing from string or file using lxml.

    Auto-selects parsing method based on content size:
        - Small HTML (<1MB) → standard parsing (fast)
        - Large HTML (>1MB) → lazy parsing with iterparse (memory-efficient)
    """
    # Handle file path
    if isinstance(html_content, str) and os.path.exists(html_content) and os.path.isfile(html_content):
        try:
            html_content = read_file(html_content, encoding)
        except FileError:
            raise
        except Exception as e:
            raise ParserError(f"Failed to read HTML file {html_content}: {str(e)}")

    validate_input(html_content)

    # Decode bytes
    if isinstance(html_content, bytes):
        if not encoding:
            from .utils import detect_encoding
            encoding = detect_encoding(html_content)
        html_content = html_content.decode(encoding, errors='replace')

    # Normalize content
    if normalize:
        html_content = normalize_html(html_content)
        if remove_scripts:
            html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        if remove_styles:
            html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        if remove_noscript:
            html_content = re.sub(r'<noscript.*?</noscript>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        if remove_comments:
            html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)

    # Auto-detect large HTML
    is_large_html = len(html_content) > 1_000_000  # 1MB threshold

    parser_args = {'recover': recover, 'encoding': encoding or 'utf-8'}
    parser_args.update(parser_kwargs)

    try:
        if is_large_html:
            # Lazy parsing for very large documents
            import io
            try:
                stream = io.BytesIO(html_content.encode(parser_args['encoding']))
                context = etree.iterparse(stream, events=("start", "end"), html=True, recover=recover)
                for event, elem in context:
                    pass
                root = context.root
                del context
                return root
            except Exception as e:
                raise ParserError(f"Lazy parse failed: {str(e)}")
        else:
            parser = html.HTMLParser(**parser_args)
            doc = html.fromstring(html_content, parser=parser)
            return doc

    except etree.ParseError as e:
        raise ParserError(f"Failed to parse HTML: {str(e)}")
    except Exception as e:
        raise ParserError(f"Unexpected error during HTML parsing: {str(e)}")


def selectors(element: Any, selector: str, method: str = "xpath") -> List[Any]:
    """Find all elements matching the selector."""
    validate_element(element)
    validate_input(selector, str)

    if method not in ["xpath", "css"]:
        raise SelectorError("Method must be 'xpath' or 'css'")

    try:
        if method == "xpath":
            return element.xpath(selector)
        else:
            return element.cssselect(selector)
    except etree.XPathError as e:
        raise SelectorError(f"Invalid XPath expression '{selector}': {str(e)}")
    except Exception as e:
        raise SelectorError(f"Selector execution failed: {str(e)}")


def selector(element: Any, selector: str, method: str = "xpath") -> Optional[Any]:
    """Find first element matching the selector."""
    results = selectors(element, selector, method)
    return results[0] if results else None


def get_selector_text(element: Any, separator: str = " ", preserve_line_breaks: bool = False) -> str:
    """Extract clean text from an element."""
    try:
        if hasattr(element, 'text_content'):
            text = element.text_content()
        else:
            text = str(element)

        if preserve_line_breaks:
            text = re.sub(r'\s+', ' ', text)
            text = text.replace('\n', ' [LINEBREAK] ')
        else:
            text = ' '.join(text.split())

        return text.strip()
    except Exception:
        return ""


def get_attr_value(element: Any, attributes: List[str]) -> Dict[str, str]:
    """Extract multiple attributes from an element."""
    result = {}
    for attr in attributes:
        try:
            result[attr] = element.get(attr) or ""
        except Exception:
            result[attr] = ""
    return result


def extract_links(element: Any, include_text: bool = True, include_title: bool = True) -> List[Dict]:
    """Extract all links from element."""
    links = selectors(element, "//a[@href]", "xpath")
    result = []

    for link in links:
        href = link.get('href') or ""
        link_data = {
            'url': href,
            'text': get_selector_text(link) if include_text else "",
            'title': link.get('title') if include_title else "",
            'attributes': dict(link.attrib)
        }
        result.append(link_data)

    return result


def get_metadata(document: Any) -> Dict[str, str]:
    """Extract metadata from HTML document."""
    metadata = {}
    title_elem = selector(document, "//title")
    if title_elem:
        metadata['title'] = get_selector_text(title_elem)

    meta_tags = selectors(document, "//meta")
    for meta in meta_tags:
        name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
        content = meta.get('content')
        if name and content:
            metadata[name.lower()] = content

    return metadata


def get_selector_tables(
    element: Any,
    include_headers: bool = True,
    as_dicts: bool = False,
    skip_empty_rows: bool = True
) -> List[Union[List[List[str]], List[Dict[str, str]]]]:
    """Extract tables from HTML content."""
    validate_element(element)
    tables = selectors(element, "//table")
    result = []

    for table in tables:
        rows = []
        header = []

        if include_headers and as_dicts:
            header_cells = selectors(table, ".//th")
            header = [safe_get_selector_text(cell).strip() for cell in header_cells]

        table_rows = selectors(table, ".//tr")
        for row in table_rows:
            cells = selectors(row, ".//td")
            if not cells and not include_headers:
                continue

            cell_texts = [safe_get_selector_text(cell).strip() for cell in cells]
            if skip_empty_rows and not any(cell_texts):
                continue

            if as_dicts and header:
                row_dict = {header[i] if i < len(header) else f"column_{i}": cell_texts[i] for i in range(len(cell_texts))}
                rows.append(row_dict)
            else:
                rows.append(cell_texts)

        result.append(rows)

    return result

# -------------------------------
# DOM Navigation Helpers
# -------------------------------

def get_parent(element: Any) -> Optional[Any]:
    """
    Get the parent of the given element.

    Args:
        element: HTML element

    Returns:
        Parent element or None
    """
    validate_element(element)
    return element.getparent()


def get_children(element: Any) -> List[Any]:
    """
    Get all direct children of the element.

    Args:
        element: HTML element

    Returns:
        List of child elements
    """
    validate_element(element)
    return list(element)


def get_next_sibling(element: Any) -> Optional[Any]:
    """
    Get the next sibling element.

    Args:
        element: HTML element

    Returns:
        Next sibling element or None
    """
    validate_element(element)
    return element.getnext()


def get_prev_sibling(element: Any) -> Optional[Any]:
    """
    Get the previous sibling element.

    Args:
        element: HTML element

    Returns:
        Previous sibling element or None
    """
    validate_element(element)
    return element.getprevious()


def get_ancestors(element: Any) -> List[Any]:
    """
    Get all ancestor elements up to the root.

    Args:
        element: HTML element

    Returns:
        List of ancestor elements
    """
    validate_element(element)
    ancestors = []
    parent = element.getparent()
    while parent is not None:
        ancestors.append(parent)
        parent = parent.getparent()
    return ancestors

# -------------------------------
# Convert all relative URLs in the element to absolute URLs.
# -------------------------------
def get_absolute_urls(
    element: Any,
    base_url: str,
    tags: Optional[List[str]] = None,
    attr_names: Optional[List[str]] = None
) -> None:
    """
    Convert all relative URLs in the element to absolute URLs.

    Args:
        element: HTML element to process
        base_url: Base URL to resolve relative paths
        tags: List of HTML tags to process (default: ['a', 'img', 'link', 'script'])
        attr_names: Attributes containing URLs (default: ['href', 'src'])

    Returns:
        None (modifies the element in-place)
    """
    validate_element(element)

    tags = tags or ["a", "img", "link", "script"]
    attr_names = attr_names or ["href", "src"]

    for tag in tags:
        for el in element.xpath(f".//{tag}"):
            for attr in attr_names:
                url = el.get(attr)
                if url and not url.startswith(("http://", "https://", "//")):
                    el.set(attr, urljoin(base_url, url))

# 👇 Explicitly define the public API
__all__ = [
    "parse_html",
    "selectors",
    "selector",
    "get_selector_text",
    "get_attr_value",
    "extract_links",
    "get_metadata",
    "get_selector_tables",
    "get_parent",
    "get_children",
    "get_next_sibling",
    "get_prev_sibling",
    "get_ancestors",
]