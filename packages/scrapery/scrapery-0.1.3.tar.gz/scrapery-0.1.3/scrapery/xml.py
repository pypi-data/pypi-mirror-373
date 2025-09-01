# xml.py

import os
from typing import Dict, List, Optional, Any, Union
from lxml import etree
from .utils import validate_input, read_file
from .exceptions import ParserError, SelectorError, FileError, ValidationError


def parse_xml(
    xml_content: str,
    encoding: Optional[str] = None,
    recover: bool = False,
    huge_tree: bool = False,
    **parser_kwargs
) -> etree._Element:
    """
    Parse XML content or file path with lxml.

    Auto-selects parsing method based on content size:
        - Small XML (<1MB) → etree.fromstring (fast)
        - Large XML (>1MB) → iterparse (memory-efficient)
    """
    # Handle file path
    if isinstance(xml_content, str) and os.path.exists(xml_content) and os.path.isfile(xml_content):
        try:
            xml_content = read_file(xml_content, encoding)
        except FileError:
            raise
        except Exception as e:
            raise ParserError(f"Failed to read XML file {xml_content}: {str(e)}")

    validate_input(xml_content)

    # Decode bytes
    if isinstance(xml_content, bytes):
        if not encoding:
            from .utils import detect_encoding
            encoding = detect_encoding(xml_content)
        xml_content = xml_content.decode(encoding, errors='replace')

    # Auto-detect large XML
    is_large_xml = len(xml_content) > 1_000_000  # 1MB threshold
    parser_args = {'recover': recover, 'huge_tree': huge_tree}
    parser_args.update(parser_kwargs)

    try:
        if is_large_xml:
            # Lazy parsing for large XML
            import io
            stream = io.BytesIO(xml_content.encode(encoding or 'utf-8'))
            context = etree.iterparse(stream, events=("start", "end"))
            for event, elem in context:
                pass
            root = context.root
            del context
            return root
        else:
            parser = etree.XMLParser(**parser_args)
            return etree.fromstring(xml_content.encode(encoding or 'utf-8'), parser=parser)
    except etree.ParseError as e:
        raise ParserError(f"Failed to parse XML: {str(e)}")
    except Exception as e:
        raise ParserError(f"Unexpected error during XML parsing: {str(e)}")


def find_xml_all(element: Any, xpath: str) -> List[Any]:
    """Find all elements matching the XPath."""
    if not isinstance(element, etree._Element):
        raise ValidationError("Invalid XML element provided")
    validate_input(xpath, str)

    try:
        return element.xpath(xpath)
    except etree.XPathError as e:
        raise SelectorError(f"Invalid XPath expression '{xpath}': {str(e)}")
    except Exception as e:
        raise SelectorError(f"XPath execution failed: {str(e)}")


def find_xml_first(element: Any, xpath: str) -> Optional[Any]:
    """Find first element matching the XPath."""
    results = find_xml_all(element, xpath)
    return results[0] if results else None


def xml_to_dict(
    element: Any,
    include_attributes: bool = True,
    include_text: bool = True
) -> Dict:
    """
    Convert XML element to dictionary efficiently.

    Uses iterative traversal to avoid recursion depth issues for very large XMLs.
    """
    validate_input(element)
    if not isinstance(element, etree._Element):
        raise ValidationError("Invalid XML element provided")

    result: Dict[str, Any] = {}
    stack = [(element, result)]

    while stack:
        current_elem, current_dict = stack.pop()

        # Element tag
        current_dict['tag'] = current_elem.tag

        # Attributes
        if include_attributes:
            current_dict['attributes'] = dict(current_elem.attrib)

        # Text content
        text = current_elem.text.strip() if current_elem.text and include_text else ""
        if text:
            current_dict['text'] = text

        # Children
        children_list = []
        current_dict['children'] = children_list
        for child in reversed(list(current_elem)):
            child_dict: Dict[str, Any] = {}
            children_list.append(child_dict)
            stack.append((child, child_dict))

    return result


def validate_xml(xml_content: str, schema_content: Optional[str] = None) -> bool:
    """Validate XML against optional schema."""
    try:
        doc = parse_xml(xml_content)
        if schema_content:
            schema = etree.XMLSchema(parse_xml(schema_content))
            return schema.validate(doc)
        return True
    except Exception:
        return False

# 👇 Explicitly define the public API for xml.py
__all__ = [
    "parse_xml",
    "find_xml_all",
    "find_xml_first",
    "xml_to_dict",
    "validate_xml",
]        