# html.py
import os
import re
from urllib.parse import urljoin
from typing import Dict, List, Optional, Any, Union
from lxml import html, etree
from .utils import validate_input, validate_element, read_file, normalize_html, standardized_string
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


def prettify(element: Any, encoding: str = "unicode") -> str:
    """
    Pretty-print an HTML element or document, similar to BeautifulSoup's prettify().
    Handles errors gracefully.
    """
    if element is None:
        raise ParserError("Cannot prettify: element is None")

    try:
        # If string input, try to parse it
        if isinstance(element, str):
            element = html.fromstring(element)

        # Serialize with pretty formatting
        result = etree.tostring(
            element,
            pretty_print=True,
            method="html",
            encoding=encoding
        )

        # Return decoded string if not unicode
        if encoding == "unicode":
            return result
        return result.decode(encoding, errors="replace")

    except etree.XMLSyntaxError as e:
        raise ParserError(f"Invalid HTML content for prettify: {str(e)}") from e
    except Exception as e:
        raise ScraperyError(f"Prettify failed: {str(e)}") from e

def _detect_selector_method(selector: str) -> str:
    """
    Detect whether the selector is XPath or CSS with robust rules.
    """
    selector = selector.strip()

    # Strong XPath signals
    xpath_signals = ["//", ".//", "/", "@", "contains(", "starts-with(", "text()", "::", "[", "]"]

    if any(sig in selector for sig in xpath_signals):
        return "xpath"

    # Default fallback → CSS
    return "css"

def selectors(element: Any, selector: str) -> List[Any]:
    """Find all elements matching the selector."""
    validate_element(element)
    validate_input(selector, str)

    if not selector or not isinstance(selector, str):
        raise ValueError("Selector must be a non-empty string")

    try:
        method = _detect_selector_method(selector)
        if method == "xpath":
            return element.xpath(selector)
        else:
           return element.cssselect(selector)

    except etree.XPathError as e:
        raise SelectorError(f"Invalid XPath expression '{selector}': {str(e)}")
    except Exception as e:
        raise SelectorError(f"Selector execution failed: {str(e)}")

def selector(element: Any, selector: str) -> Optional[Any]:
    """Find first element matching the selector."""
    try:
        results = selectors(element, selector)
        return results[0] if results else None
    except Exception as e:
        raise RuntimeError(f"Error in find_first with selector '{selector}': {e}")

def get_selector_content(
    tree: Optional[etree._Element],
    selector: Optional[str] = None,
    attr: Optional[str] = None
) -> Optional[Union[str, List[str], List[etree._Element]]]:
    """
    Extract content from an lxml element/tree using CSS or XPath auto-detection.

    Supports multiple cases:
    1. Return text of the first matching element for selector.
    2. Return value of the specified attribute for selector.
    3. Return value of the specified attribute from the tree directly.
    4. Return text content of the entire tree if no selector or attribute is provided.

    Args:
        tree: lxml element/tree to search in.
        selector: CSS or XPath selector to find element(s).
        attr: Attribute name to extract from selected element/tree.

    Returns:
        - Text or attribute value (str)
        - List of elements if needed
        - None if no match
    """
    if tree is None:
        return None

    try:
        # Case 4: no selector provided, return full tree text or attribute
        if not selector:
            if attr:
                return standardized_string(tree.get(attr, ""))
            return standardized_string(tree.text_content())

        # Detect method
        method = _detect_selector_method(selector)

        # Fetch first matching element
        if method == "xpath":
            results = tree.xpath(selector)
        else:  # CSS
            results = tree.cssselect(selector)

        if not results:
            return None

        first = results[0]

        # If first result is element, return attribute or text
        if isinstance(first, etree._Element):
            if attr:
                return standardized_string(first.get(attr, ""))
            return standardized_string(first.text_content())
        else:
            # If XPath returns text or number directly
            return standardized_string(str(first))

    except Exception as e:
        print(f"Error in get_selector_content: {e}")
        return None

def get_attr_value(element: Any, attr: List[str]) -> str:
    """scrape attributes from an element."""
    try:
        return element.get(attr) or ""
    except Exception:
        return ""

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
            header = [get_selector_content(cell).strip() for cell in header_cells]

        table_rows = selectors(table, ".//tr")
        for row in table_rows:
            cells = selectors(row, ".//td")
            if not cells and not include_headers:
                continue

            cell_texts = [get_selector_content(cell).strip() for cell in cells]
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
# DOM Navigation Utilities
# -------------------------------
# --------------------  --------------------

def parent(element: Optional[etree._Element]) -> Optional[etree._Element]:
    """Return the parent of the element, or None if not applicable."""
    try:
        return element.getparent() if element is not None else None
    except Exception:
        return None

def children(element: Optional[etree._Element]) -> List[etree._Element]:
    """Return the list of children for the given element."""
    try:
        return list(element) if element is not None else []
    except Exception:
        return []

def siblings(element: Optional[etree._Element], include_self: bool = False) -> List[etree._Element]:
    """Return siblings of the element, optionally including the element itself."""
    try:
        if element is None or element.getparent() is None:
            return []
        sibs = list(element.getparent())
        if not include_self and element in sibs:
            sibs.remove(element)
        return sibs
    except Exception:
        return []

def next_sibling(element: Optional[etree._Element]) -> Optional[etree._Element]:
    """Return the next sibling of the element, or None if not available."""
    try:
        if element is None or element.getparent() is None:
            return None
        siblings = list(element.getparent())
        idx = siblings.index(element)
        return siblings[idx + 1] if idx + 1 < len(siblings) else None
    except Exception:
        return None

def prev_sibling(element: Optional[etree._Element]) -> Optional[etree._Element]:
    """Return the previous sibling of the element, or None if not available."""
    try:
        if element is None or element.getparent() is None:
            return None
        siblings = list(element.getparent())
        idx = siblings.index(element)
        return siblings[idx - 1] if idx > 0 else None
    except Exception:
        return None


def ancestors(element: Optional[etree._Element]) -> List[etree._Element]:
    """Return the list of ancestors of the element."""
    try:
        return list(element.iterancestors()) if element is not None else []
    except Exception:
        return []

def descendants(element: Optional[etree._Element]) -> List[etree._Element]:
    """Return the list of descendants of the element."""
    try:
        return list(element.iterdescendants()) if element is not None else []
    except Exception:
        return []


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
    "prettify",
    "selectors",
    "selector",
    "get_selector_content",
    "get_attr_value",
    "extract_links",
    "get_metadata",
    "get_selector_tables",
    "parent",
    "children",
    "siblings",
    "next_sibling",
    "prev_sibling",
    "ancestors",
    "descendants",
]