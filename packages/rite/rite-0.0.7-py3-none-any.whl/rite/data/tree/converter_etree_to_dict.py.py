# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Rite - Tree - ElementTree to Dictionary Converter Module
========================================================

Provides functionality to convert ElementTree elements to dictionaries.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from collections import defaultdict
from typing import Any, Dict, List
from xml.etree.ElementTree import Element

# Import | Libraries

# Import | Local Modules


# =============================================================================
# Functions
# =============================================================================


def convert_etree_to_dict(t: Element) -> Dict[str, Any]:
    """
    ElementTree to Dictionary Converter
    ===================================

    Convert an xml.etree.ElementTree.Element into a nested dictionary.

    Attributes are prefixed with "@" and text content is stored under "#text".

    Example:
        <node id="1">Hello</node> →
        {'node': {'@id': '1', '#text': 'Hello'}}

    Args:
        t: The ElementTree element to convert.

    Returns:
        A dictionary representation of the XML element.
    """
    result: Dict[str, Any] = {t.tag: {} if t.attrib else None}

    children = list(t)
    if children:
        grouped_children = defaultdict(list)
        for child in children:
            child_dict = convert_etree_to_dict(child)
            for key, value in child_dict.items():
                grouped_children[key].append(value)
        result[t.tag] = {
            key: value[0] if len(value) == 1 else value
            for key, value in grouped_children.items()
        }

    if t.attrib:
        result.setdefault(t.tag, {})
        result[t.tag].update({f"@{k}": v for k, v in t.attrib.items()})

    text = (t.text or "").strip()
    if text:
        if children or t.attrib:
            result[t.tag]["#text"] = text
        else:
            result[t.tag] = text

    return result


# =============================================================================
# Module Exports
# =============================================================================

__all__: List[str] = [
    "convert_etree_to_dict",
]
