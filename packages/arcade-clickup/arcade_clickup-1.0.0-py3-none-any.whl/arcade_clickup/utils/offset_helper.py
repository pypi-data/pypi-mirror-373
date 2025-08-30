"""
Offset-based retrieval utilities and interfaces for ClickUp tools.

This module provides reusable offset logic, interfaces for offset-based results,
and helper functions for consistent offset-based retrieval across all ClickUp tools.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

# Type variables for generic offset-based retrieval
T = TypeVar("T")
SortableItem = TypeVar("SortableItem", bound="Sortable")
OffsetResponseT = TypeVar("OffsetResponseT", bound="OffsetResponse")


@runtime_checkable
class Sortable(Protocol):
    """Protocol for items that can be sorted by a field."""

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to fields for sorting."""
        ...


@runtime_checkable
class OffsetResponse(Protocol):
    """Protocol for offset-based API responses."""

    success: bool
    items_returned: int
    current_offset: int
    next_offset: int
    is_last: bool


class OffsetParams:
    """Container for offset parameters with validation."""

    def __init__(self, offset: int = 0, limit: int = 50, max_limit: int = 50):
        """
        Initialize offset parameters with validation.

        Args:
            offset: Starting position (will be normalized to >= 0)
            limit: Number of items to return (will be clamped to 1 <= limit <= max_limit)
            max_limit: Maximum allowed limit value
        """
        self.offset = max(0, offset)
        self.limit = max(1, min(limit, max_limit))
        self.max_limit = max_limit

    def __repr__(self) -> str:
        return f"OffsetParams(offset={self.offset}, limit={self.limit})"


class OffsetResult(Generic[T]):
    """Container for offset calculation results."""

    def __init__(
        self,
        items: list[T],
        current_offset: int,
        limit: int,
    ):
        """
        Initialize offset result.

        Args:
            items: The retrieved items
            current_offset: The offset used for this retrieval
            limit: The limit used for this retrieval
        """
        self.items = items
        self.current_offset = current_offset
        self.actual_returned = len(items)
        self.next_offset = current_offset + self.actual_returned
        self.is_last = self.actual_returned < limit

    def to_dict(self) -> dict[str, Any]:
        """Convert offset metadata to dictionary."""
        return {
            "items_returned": self.actual_returned,
            "current_offset": self.current_offset,
            "next_offset": self.next_offset,
            "is_last": self.is_last,
        }


class OffsetHelper:
    """Reusable helper for applying offset-based retrieval and sorting to collections."""

    @staticmethod
    def offset_and_sort(
        items: list[SortableItem],
        offset_params: OffsetParams,
        sort_field: str = "name",
        sort_key_func: Callable[[SortableItem], Any] | None = None,
        reverse: bool = False,
    ) -> OffsetResult[SortableItem]:
        """
        Apply sorting and offset-based retrieval to a list of items.

        Args:
            items: List of items to retrieve and sort
            offset_params: Offset parameters
            sort_field: Field name to sort by (default: "name")
            sort_key_func: Custom sort key function (overrides sort_field)
            reverse: Whether to sort in descending order

        Returns:
            OffsetResult containing retrieved items and metadata
        """
        # Apply sorting
        if sort_key_func:
            sorted_items = sorted(items, key=sort_key_func, reverse=reverse)
        else:
            sorted_items = sorted(
                items,
                key=lambda item: _get_sort_value(item, sort_field),
                reverse=reverse,
            )

        # Apply offset-based retrieval
        start_idx = offset_params.offset
        end_idx = start_idx + offset_params.limit
        retrieved_items = sorted_items[start_idx:end_idx]

        return OffsetResult(
            items=retrieved_items,
            current_offset=offset_params.offset,
            limit=offset_params.limit,
        )

    @staticmethod
    def create_offset_response(
        result: OffsetResult,
        success: bool = True,
        **additional_fields: Any,
    ) -> dict[str, Any]:
        """
        Create a standardized offset-based response dictionary.

        Args:
            result: OffsetResult from offset_and_sort
            success: Whether the operation was successful
            **additional_fields: Additional fields to include in response

        Returns:
            Dictionary with standardized offset fields
        """
        response = {
            "success": success,
            **result.to_dict(),
            **additional_fields,
        }
        return response

    @staticmethod
    def create_simple_result(
        items: list[SortableItem],
        offset: int,
        limit: int,
        is_last: bool | None = None,
    ) -> OffsetResult[SortableItem]:
        """
        Create a simple OffsetResult without sorting or additional processing.

        This is useful when items are already filtered/sorted by an external source
        (like an API) and you just need to package them into an OffsetResult.

        Args:
            items: Pre-filtered/sorted items
            offset: The offset that was used to retrieve these items
            limit: The limit that was requested
            is_last: Whether this is the last page (if known, overrides calculation)

        Returns:
            OffsetResult containing the items and metadata
        """
        result = OffsetResult(
            items=items,
            current_offset=offset,
            limit=limit,
        )

        # Override is_last calculation if explicitly provided
        if is_last is not None:
            result.is_last = is_last

        return result


def _get_sort_value(item: SortableItem, field: str) -> Any:
    """
    Extract sort value from an item for the given field.

    Args:
        item: Item to extract value from
        field: Field name to extract

    Returns:
        Sort value (lowercased if string, otherwise original value)
    """
    try:
        value = item[field]
        # Handle None values as empty strings to prevent comparison errors
        if value is None:
            return ""
        # Convert strings to lowercase for case-insensitive sorting
        if isinstance(value, str):
            return value.lower()
        else:
            return value
    except (KeyError, TypeError):
        # Return empty string as fallback for missing/invalid fields
        return ""
