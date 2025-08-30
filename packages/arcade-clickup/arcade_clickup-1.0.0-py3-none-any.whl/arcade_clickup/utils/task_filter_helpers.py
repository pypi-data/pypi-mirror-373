"""
Task filtering helper functions for ClickUp toolkit.

This module provides reusable functions for building task filter parameters
and executing filtered task workflows using the ClickUp API.
"""

from typing import Any

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.constants import FilterScope, TaskOrderBy
from arcade_clickup.models.api_models import FilteredTeamTasksRequest
from arcade_clickup.utils.helpers import map_task_to_tool_model
from arcade_clickup.utils.offset_helper import OffsetHelper
from arcade_clickup.utils.task_helpers import _parse_date_string_to_epoch_ms


def build_task_filter_params(
    offset: int = 0,
    limit: int = 20,
    order_by: TaskOrderBy | None = None,
    should_sort_by_reverse: bool = False,
    statuses: list[str] | None = None,
    include_closed: bool = False,
    assignees_ids: list[int] | None = None,
    space_ids: list[str] | None = None,
    folder_ids: list[str] | None = None,
    list_ids: list[str] | None = None,
    due_date_gt: str | None = None,
    due_date_lt: str | None = None,
    date_created_gt: str | None = None,
    date_created_lt: str | None = None,
) -> tuple[FilteredTeamTasksRequest, int, int]:
    """
    Build filter parameters for the ClickUp filtered team tasks endpoint.

    Args:
        offset: Starting position for results
        limit: Maximum number of tasks to return (max 50, default 20)
        order_by: Field to sort by
        should_sort_by_reverse: Whether to sort in descending order
        statuses: List of status strings to filter by
        include_closed: Whether to include closed tasks
        assignees_ids: List of assignee user IDs
        space_ids: List of space IDs to filter by
        folder_ids: List of folder IDs to filter by
        list_ids: List of list IDs to filter by
        due_date_gt: Due date greater than (date string)
        due_date_lt: Due date less than (date string)
        date_created_gt: Created date greater than (date string)
        date_created_lt: Created date less than (date string)

    Returns:
        tuple: (FilteredTeamTasksRequest, offset, limit) - typed request parameters and
            pagination info
    """
    request: FilteredTeamTasksRequest = {}

    # Normalize limit (max 50 for tools)
    normalized_limit = min(limit, 50)

    if order_by is not None:
        request["order_by"] = order_by.value

    if should_sort_by_reverse:
        request["reverse"] = "true"

    if statuses:
        request["statuses"] = statuses

    if include_closed:
        request["include_closed"] = "true"

    if assignees_ids:
        request["assignees"] = assignees_ids

    if space_ids:
        request["space_ids"] = space_ids

    if folder_ids:
        request["folder_ids"] = folder_ids

    if list_ids:
        request["list_ids"] = list_ids

    # Convert date strings to epoch milliseconds
    _add_date_params(
        request,
        due_date_gt=due_date_gt,
        due_date_lt=due_date_lt,
        date_created_gt=date_created_gt,
        date_created_lt=date_created_lt,
    )

    return request, offset, normalized_limit


async def execute_filtered_tasks_workflow(
    api_client: ClickupApiClient,
    workspace_id: str,
    request: FilteredTeamTasksRequest,
    offset: int,
    limit: int,
    filter_context: str = "workspace",
) -> dict[str, Any]:
    """
    Execute the filtered tasks workflow using the ClickUp API.

    This is a reusable workflow function that handles the common pattern
    of filtering tasks, mapping them to tool models, and building responses.

    Args:
        api_client: ClickUp API client
        workspace_id: The workspace/team ID
        request: Typed request parameters for filtering
        offset: Starting position for pagination
        limit: Maximum number of items to return
        filter_context: Context description for logging (e.g., "workspace", "space")

    Returns:
        dict: Response with filtered tasks and metadata
    """
    api_response = await api_client.get_filtered_team_tasks(
        workspace_id=workspace_id,
        request=request,
        offset=offset,
        limit=limit,
    )

    raw_tasks = api_response["tasks"]
    all_tasks = [map_task_to_tool_model(task, workspace_id) for task in raw_tasks]

    is_last_page = api_response.get("is_last_page", True)  # Default to True if not provided

    offset_result = OffsetHelper.create_simple_result(
        items=all_tasks,
        offset=offset,
        limit=limit,
        is_last=is_last_page,
    )

    response = OffsetHelper.create_offset_response(
        result=offset_result,
        success=True,
        workspace_id=workspace_id,
        tasks=offset_result.items,
        filter_context=filter_context,
    )

    return response


def _build_scoped_filter_params(
    scope: FilterScope,
    item_ids: list[str] | None = None,
    offset: int = 0,
    limit: int = 20,
    **kwargs: Any,
) -> tuple[FilteredTeamTasksRequest, int, int]:
    """Build filter params for scoped task filtering (all/spaces/folders/lists)."""
    if scope == FilterScope.ALL:
        # For "ALL" scope, no specific IDs needed - filter across entire workspace
        return build_task_filter_params(offset=offset, limit=limit, **kwargs)
    elif scope == FilterScope.SPACES:
        if not item_ids:
            msg = "item_ids required for SPACES scope"
            raise ValueError(msg)
        return build_task_filter_params(offset=offset, limit=limit, space_ids=item_ids, **kwargs)
    elif scope == FilterScope.FOLDERS:
        if not item_ids:
            msg = "item_ids required for FOLDERS scope"
            raise ValueError(msg)
        return build_task_filter_params(offset=offset, limit=limit, folder_ids=item_ids, **kwargs)
    elif scope == FilterScope.LISTS:
        if not item_ids:
            msg = "item_ids required for LISTS scope"
            raise ValueError(msg)
        return build_task_filter_params(offset=offset, limit=limit, list_ids=item_ids, **kwargs)
    else:
        msg = f"Unsupported filter scope: {scope}"
        raise ValueError(msg)


def _build_assignees_filter_params(
    assignees_ids: list[int],
    offset: int = 0,
    limit: int = 20,
    **kwargs: Any,
) -> tuple[FilteredTeamTasksRequest, int, int]:
    """Build filter params for assignees task filtering."""
    return build_task_filter_params(
        offset=offset, limit=limit, assignees_ids=assignees_ids, **kwargs
    )


def _add_date_params(
    normalized_params: FilteredTeamTasksRequest, **date_params: str | None
) -> None:
    """Add normalized date parameters to the request."""

    due_date_gt = date_params.get("due_date_gt")
    if due_date_gt is not None:
        timestamp, _ = _parse_date_string_to_epoch_ms(due_date_gt)
        normalized_params["due_date_gt"] = timestamp

    due_date_lt = date_params.get("due_date_lt")
    if due_date_lt is not None:
        timestamp, _ = _parse_date_string_to_epoch_ms(due_date_lt)
        normalized_params["due_date_lt"] = timestamp

    date_created_gt = date_params.get("date_created_gt")
    if date_created_gt is not None:
        timestamp, _ = _parse_date_string_to_epoch_ms(date_created_gt)
        normalized_params["date_created_gt"] = timestamp

    date_created_lt = date_params.get("date_created_lt")
    if date_created_lt is not None:
        timestamp, _ = _parse_date_string_to_epoch_ms(date_created_lt)
        normalized_params["date_created_lt"] = timestamp
