"""Fuzzy search tools for ClickUp resources."""

from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import ClickUp
from arcade_tdk.errors import RetryableToolError, ToolExecutionError

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.constants import (
    FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    FUZZY_SEARCH_MAX_PAGES,
    FUZZY_SEARCH_MIN_QUERY_LENGTH,
)
from arcade_clickup.utils import fuzzy_search_helpers
from arcade_clickup.utils.helpers import clean_dict


@tool(requires_auth=ClickUp())
async def fuzzy_search_tasks_by_name(
    context: ToolContext,
    name_to_search: Annotated[
        str,
        f"Task name to search for (minimum {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters)",
    ],
    workspace_id: Annotated[str, "The workspace ID to search tasks in (should be a number)"],
    scan_size: Annotated[
        int,
        f"Number of recent tasks to scan (max {FUZZY_SEARCH_MAX_PAGES * 100} "
        f"default: {FUZZY_SEARCH_DEFAULT_SCAN_SIZE})",
    ] = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    include_closed: Annotated[bool, "Include closed/completed tasks (default: false)"] = False,
    statuses: Annotated[
        list[str] | None,
        "Filter by specific ClickUp status names. Each list has its own statuses set.",
    ] = None,
    assignee_ids: Annotated[
        list[str] | None,
        "Filter by assignee user IDs",
    ] = None,
    space_ids: Annotated[
        list[str] | None,
        "Filter by ClickUp space IDs - limit search to specific spaces/teams",
    ] = None,
    folder_ids: Annotated[
        list[str] | None,
        "Filter by ClickUp folder IDs - limit search to specific folders/projects",
    ] = None,
    list_ids: Annotated[
        list[str] | None,
        "Filter by ClickUp list IDs - limit search to specific lists",
    ] = None,
    limit: Annotated[int, "Maximum number of matches to return (max: 50, default: 10)"] = 10,
) -> Annotated[dict[str, Any], "Fuzzy search results for tasks"]:
    """
    Search for tasks using fuzzy matching on task names.

    This tool should ONLY be used when you cannot find the desired task through normal context
    or direct searches. It performs fuzzy matching against task names and returns simplified
    task information. Use the returned task IDs with get_task_by_id to retrieve full task details.

    This tool is also useful to avoid navigating through the ClickUp hierarchy tree
    when you know approximately what task you're looking for
    but don't know its exact location in the hierarchy.

    Returns the most recently updated tasks that match the name_to_search with match scores
    indicating relevance (1.0 = perfect match, lower scores = less relevant matches).
    """
    # Validate inputs
    if len(name_to_search) < FUZZY_SEARCH_MIN_QUERY_LENGTH:
        msg = f"Query must be at least {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters long"
        raise ToolExecutionError(msg)

    limit = _validate_limit(limit, max_allowed=50)

    client = ClickupApiClient(context)

    filters: dict[str, Any] = {
        "include_closed": str(include_closed).lower(),
    }

    if statuses:
        filters["statuses"] = statuses
    if assignee_ids:
        filters["assignees"] = assignee_ids
    if space_ids:
        filters["space_ids"] = space_ids
    if folder_ids:
        filters["folder_ids"] = folder_ids
    if list_ids:
        filters["list_ids"] = list_ids

    result = await fuzzy_search_helpers.execute_fuzzy_search_tasks_workflow(
        client=client,
        workspace_id=workspace_id,
        query=name_to_search,
        scan_size=scan_size,
        filters=filters,
        limit=limit,
    )
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def fuzzy_search_lists_by_name(
    context: ToolContext,
    name_to_search: Annotated[
        str,
        f"List name to search for (minimum {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters)",
    ],
    workspace_id: Annotated[str, "The workspace ID to search lists in (should be a number)"],
    scan_size: Annotated[
        int,
        f"Number of lists to scan (in increments of 100, max {FUZZY_SEARCH_MAX_PAGES * 100} "
        f"default: {FUZZY_SEARCH_DEFAULT_SCAN_SIZE})",
    ] = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    space_ids: Annotated[
        list[str] | None,
        "Filter by ClickUp space IDs - limit search to specific spaces/teams",
    ] = None,
    folder_ids: Annotated[
        list[str] | None,
        "Filter by ClickUp folder IDs - limit search to specific folders/projects",
    ] = None,
    should_include_archived: Annotated[bool, "Include archived lists (default: false)"] = False,
    limit: Annotated[int, "Maximum number of matches to return (max: 50, default: 10)"] = 10,
) -> Annotated[dict[str, Any], "Fuzzy search results for lists"]:
    """
    Search for lists using fuzzy matching on list names.

    This tool should ONLY be used when you cannot find the desired list through normal context
    or direct searches. It performs fuzzy matching against list names and returns simplified
    list information. Use other ClickUp tools to get full list details or work with the lists.

    This tool is also useful to avoid navigating through the ClickUp hierarchy tree
    when you know approximately what list you're looking for
    but don't know its exact location in the hierarchy.

    Returns lists that match the name_to_search with match scores indicating relevance
    (1.0 = perfect match, lower scores = less relevant matches).
    """
    # Validate inputs
    if len(name_to_search) < FUZZY_SEARCH_MIN_QUERY_LENGTH:
        msg = f"Query must be at least {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters long"
        raise ToolExecutionError(msg)

    limit = _validate_limit(limit, max_allowed=50)

    client = ClickupApiClient(context)
    result = await fuzzy_search_helpers.execute_fuzzy_search_lists_workflow(
        client=client,
        workspace_id=workspace_id,
        query=name_to_search,
        scan_size=scan_size,
        space_ids=space_ids,
        folder_ids=folder_ids,
        archived=should_include_archived,
        limit=limit,
    )
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def fuzzy_search_folders_by_name(
    context: ToolContext,
    name_to_search: Annotated[
        str,
        f"Folder name to search for (minimum {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters)",
    ],
    workspace_id: Annotated[str, "The workspace ID to search folders in (should be a number)"],
    scan_size: Annotated[
        int,
        f"Number of folders to scan (in increments of 100, max {FUZZY_SEARCH_MAX_PAGES * 100} "
        f"default: {FUZZY_SEARCH_DEFAULT_SCAN_SIZE})",
    ] = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    space_ids: Annotated[
        list[str] | None,
        "Filter by ClickUp space IDs - limit search to specific spaces/teams",
    ] = None,
    should_include_archived: Annotated[bool, "Include archived folders (default: false)"] = False,
    limit: Annotated[int, "Maximum number of matches to return (max: 50, default: 10)"] = 10,
) -> Annotated[dict[str, Any], "Fuzzy search results for folders"]:
    """
    Search for folders using fuzzy matching on folder names.

    This tool should ONLY be used when you cannot find the desired folder through normal context
    or direct searches. It performs fuzzy matching against folder names and returns simplified
    folder information. Use other ClickUp tools to get full folder details or work with the folders.

    This tool is also useful to avoid navigating through the ClickUp hierarchy tree
    when you know approximately what folder/project you're looking for
    but don't know its exact location in the hierarchy.

    In ClickUp, folders are also known as projects and serve as organizational containers for lists.
    Returns folders that match the name_to_search with match scores indicating relevance
    (1.0 = perfect match, lower scores = less relevant matches).
    """
    # Validate inputs
    if len(name_to_search) < FUZZY_SEARCH_MIN_QUERY_LENGTH:
        msg = f"Query must be at least {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters long"
        raise ToolExecutionError(msg)

    limit = _validate_limit(limit, max_allowed=50)

    client = ClickupApiClient(context)
    result = await fuzzy_search_helpers.execute_fuzzy_search_folders_workflow(
        client=client,
        workspace_id=workspace_id,
        query=name_to_search,
        scan_size=scan_size,
        space_ids=space_ids,
        archived=should_include_archived,
        limit=limit,
    )
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def fuzzy_search_members_by_name(
    context: ToolContext,
    name_to_search: Annotated[
        str,
        f"Member name to search for (minimum {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters)",
    ],
    workspace_id: Annotated[str, "The workspace ID to search members in (should be a number)"],
    scan_size: Annotated[
        int,
        f"Number of members to scan (in increments of 100, max {FUZZY_SEARCH_MAX_PAGES * 100} "
        f"default: {FUZZY_SEARCH_DEFAULT_SCAN_SIZE})",
    ] = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    limit: Annotated[int, "Maximum number of matches to return (max: 50, default: 10)"] = 10,
) -> Annotated[dict[str, Any], "Fuzzy search results for members"]:
    """
    Search for workspace members using fuzzy matching on member names.

    This tool should ONLY be used when you cannot find the desired team member through
    normal context
    It performs fuzzy matching against member names and returns
    simplified member information including ID, name, and email.

    Returns team members that match the name_to_search with match scores indicating
    relevance (1.0 = perfect match, lower scores = less relevant matches).
    """
    # Validate inputs
    if len(name_to_search) < FUZZY_SEARCH_MIN_QUERY_LENGTH:
        msg = f"Query must be at least {FUZZY_SEARCH_MIN_QUERY_LENGTH} characters long"
        raise ToolExecutionError(msg)

    limit = _validate_limit(limit, max_allowed=50)

    client = ClickupApiClient(context)
    result = await fuzzy_search_helpers.execute_fuzzy_search_members_workflow(
        client=client,
        workspace_id=workspace_id,
        query=name_to_search,
        scan_size=scan_size,
        limit=limit,
    )
    return clean_dict(dict(result))


def _validate_limit(limit: int, max_allowed: int = 50) -> int:
    """
    Validate and normalize limit parameter.

    Args:
        limit: The requested number of matches
        max_allowed: The maximum allowed value for this tool

    Returns:
        Validated limit value (minimum 1)

    Raises:
        RetryableToolError: If limit exceeds max_allowed
    """
    if limit <= 0:
        return 1
    elif limit > max_allowed:
        msg = f"limit must be between 1 and {max_allowed}"
        raise RetryableToolError(
            message=msg,
            additional_prompt_content=(
                f"Please provide a limit value between 1 and {max_allowed}."
            ),
            retry_after_ms=0,
        )
    return limit
