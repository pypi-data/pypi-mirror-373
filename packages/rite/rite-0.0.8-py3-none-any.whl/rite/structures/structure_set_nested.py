# -*- coding: utf-8 -*-


# =============================================================================
# Docstring
# =============================================================================

"""
Nested Set Structure Module
===========================

This module provides a `NestedSetStructure` class that allows for the
management of hierarchical relationships between items. It supports
adding items with parent-child relationships, retrieving children and parents,
and provides a way to retrieve all items in a nested, flattened order.

"""


# =============================================================================
# Imports
# =============================================================================

# Import | Future
from __future__ import annotations

# Import | Standard Library
from collections import defaultdict
from typing import Any, Dict, Iterator, List, Optional

# =============================================================================
# Classes
# =============================================================================


class NestedSetStructure:
    """
    Nested Set Structure Class
    ==========================

    A structure to track items and their hierarchical relationships.
    Supports multi-level trees with parent/child tracking. Useful for
    scenarios like recursive publishing, dependency resolution, or
    graph-like traversal.

    """

    def __init__(self) -> None:
        """
        Initialize the nested set structure.
        """
        self._root_elements: List[Any] = []
        self._children: Dict[Any, List[Any]] = defaultdict(list)
        self._parent: Dict[Any, Optional[Any]] = {}

    def __contains__(self, item: Any) -> bool:
        """
        Check if an item is in the structure.
        """
        return item in self._children

    def __len__(self) -> int:
        """
        Return the number of children.
        """
        return len(self._children)

    def __iter__(self) -> Iterator:
        """
        Return an iterator over the children.
        """
        return iter(self._children)

    def add(
        self,
        item: Any,
        parent: Optional[Any] = None,
    ) -> None:
        """
        Add an item to the structure, optionally specifying a parent.
        """
        if item in self._children:
            # already added
            return

        if parent is None:
            self._root_elements.append(item)
        else:
            self._children[parent].append(item)
            self._parent[item] = parent

        self._children[item] = self._children.get(item, [])

    def children(self, item: Any) -> List[Any]:
        """
        Return the children of the given item.
        If the item has no children, returns an empty list.
        """
        return self._children.get(item, [])

    def parent(self, item: Any) -> Optional[Any]:
        """
        Return the parent of the given item, or None if it has no parent.
        """
        return self._parent.get(item)

    def original(self, item: Any) -> Any:
        """
        Return the original object stored in the set that equals `item`,
        or `item` itself if not found. This is useful for matching
        back to canonical instances.
        """
        for existing in self._children:
            if existing == item:
                return existing
        return item

    def nested_items(self) -> List[Any]:
        """
        Return a nested, flattened list of items (including children)
        in insertion order. Maintains hierarchy order.
        """
        items: List[Any] = []
        self._add_nested_items(self._root_elements, items)
        return items

    def _add_nested_items(
        self,
        items: List[Any],
        nested: List[Any],
    ) -> None:
        """
        Recursively add items and their children to the nested list.
        """
        for item in items:
            nested.append(item)
            children = self.children(item)
            if children:
                self._add_nested_items(children, nested)


# =============================================================================
# Module Exports
# =============================================================================

__all__: List[str] = [
    "NestedSetStructure",
]
