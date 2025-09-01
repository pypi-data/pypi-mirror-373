from typing import TypeVar
from xml.etree.ElementTree import Element

T = TypeVar("T")


def get_attribute(
    xml_element: Element, attribute_name: str, default: T = None
) -> str | T:
    """Returns the value of the attribute with the given name from the XML element,
    or the default value if not found.

    This respects the BEAST 2 XML format, where an attribute can also be specified
    using a child element with the same name as the attribute or an input element with
    the name attribute set to the attribute name."""

    if attribute := xml_element.attrib.get(attribute_name):
        return attribute

    for child in xml_element:
        if child.tag == attribute_name and child.text:
            return child.text

        if (
            child.tag == "input"
            and child.attrib.get("name") == attribute_name
            and child.text
        ):
            return child.text

    return default
