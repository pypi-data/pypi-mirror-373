"""
Task management tools for ClickUp.
"""

from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import ClickUp
from arcade_tdk.errors import ToolExecutionError

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.constants import FilterScope, TaskOrderBy, TaskPriority
from arcade_clickup.utils.helpers import (
    clean_dict,
    map_task_to_tool_model,
    validate_workspace_id_and_raise,
)
from arcade_clickup.utils.task_filter_helpers import (
    _build_assignees_filter_params,
    _build_scoped_filter_params,
    execute_filtered_tasks_workflow,
)
from arcade_clickup.utils.task_helpers import (
    build_assignee_update_payload,
    build_create_task_payload,
    build_update_task_payload,
    create_task_creation_result,
    create_task_update_result,
    map_task_assignee_update_to_tool_result,
)


@tool(requires_auth=ClickUp())
async def create_task(
    context: ToolContext,
    list_id: Annotated[str, "The ClickUp list ID where the task will be created"],
    task_title: Annotated[str, "The name/title of the task"],
    description: Annotated[str, "The description/content of the task"] = "",
    priority: Annotated[TaskPriority | None, "Task priority"] = None,
    status: Annotated[str | None, "Task status label (string)"] = None,
    parent_task_id: Annotated[str | None, "The parent task ID if this is a subtask"] = None,
    start_date: Annotated[
        str | None,
        "Date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS]; ISO-8601 also supported",
    ] = None,
    due_date: Annotated[
        str | None,
        "Date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS]; ISO-8601 also supported",
    ] = None,
    sprint_points: Annotated[int | None, "The sprint points for the task"] = None,
) -> Annotated[dict[str, Any], "Details of the created task"]:
    """Create a new task in a ClickUp list with optional planning metadata.

    Use this tool when you want to add a task to a specific list and optionally set
    its initial status, priority, scheduling information, and hierarchy.
    """
    api_client = ClickupApiClient(context)
    task_data = build_create_task_payload(
        name=task_title,
        description=description,
        priority=priority,
        status=status,
        parent_task_id=parent_task_id,
        start_date=start_date,
        due_date=due_date,
        points=sprint_points,
    )

    api_response = await api_client.create_task(list_id, task_data)
    tool_task = map_task_to_tool_model(api_response)  # type: ignore[arg-type]

    result = create_task_creation_result(tool_task, task_title)
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def get_task_by_id(
    context: ToolContext,
    task_id: Annotated[str, "The task ID or custom task ID to retrieve"],
    include_subtasks: Annotated[bool, "Include subtask information (default: false )"] = False,
    workspace_id_for_custom_id: Annotated[
        str | None, "The ClickUp workspace ID (provide this to use custom task IDs)"
    ] = None,
) -> Annotated[dict[str, Any], "The detailed task response"]:
    """
    Get detailed information about a specific task by its ID. Also supports custom task IDs
    when workspace_id_for_custom_id is provided.

    Use when need more information about a task than if it id or custom id is already known.
    """
    client = ClickupApiClient(context)

    if workspace_id_for_custom_id is not None:
        validate_workspace_id_and_raise(workspace_id_for_custom_id)

    response = await client.get_task_by_id(
        task_id=task_id,
        include_subtasks=include_subtasks,
        custom_task_ids=workspace_id_for_custom_id is not None,
        team_id=workspace_id_for_custom_id,
    )

    task = map_task_to_tool_model(response)  # type: ignore[arg-type]

    return clean_dict(dict(task))


@tool(requires_auth=ClickUp())
async def update_task(
    context: ToolContext,
    task_id: Annotated[str, "The ClickUp task ID to update"],
    task_title: Annotated[str | None, "The new name/title of the task"] = None,
    description: Annotated[str | None, "The new description/content of the task"] = None,
    priority: Annotated[TaskPriority | None, "Task priority"] = None,
    status: Annotated[str | None, "Task status label (string)"] = None,
    parent_task_id: Annotated[str | None, "The new parent task ID"] = None,
    start_date: Annotated[
        str | None,
        "Date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS]; ISO-8601 also supported",
    ] = None,
    due_date: Annotated[
        str | None,
        "Date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS]; ISO-8601 also supported",
    ] = None,
    sprint_points: Annotated[int | None, "The new sprint points for the task"] = None,
) -> Annotated[dict[str, Any], "Details of the updated task"]:
    """Update one or more fields of an existing ClickUp task.

    Use this tool to change a task's title, description, status, priority, dates,
    hierarchy (by setting a new parent), or sprint points. You can pass only the
    fields you want to modify—everything else remains unchanged.
    """
    api_client = ClickupApiClient(context)
    update_data = build_update_task_payload(
        name=task_title,
        description=description,
        priority=priority,
        status=status,
        parent_task_id=parent_task_id,
        start_date=start_date,
        due_date=due_date,
        points=sprint_points,
    )

    if not update_data:
        result = create_task_update_result(
            error_message="No fields provided to update. At least one field must be provided "
            + "to update the task."
        )
        return clean_dict(dict(result))

    api_response = await api_client.update_task(task_id, update_data)
    tool_task = map_task_to_tool_model(api_response)  # type: ignore[arg-type]

    result = create_task_update_result(tool_task, task_id)
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def get_tasks_by_scope(
    context: ToolContext,
    workspace_id: Annotated[
        str, "The ClickUp workspace ID for GUI URL generation (should be a number)"
    ],
    scope: Annotated[FilterScope, "The scope to filter tasks by (all, spaces, folders, or lists)"],
    item_ids: Annotated[
        list[str] | None,
        "List of IDs to get tasks from (required for spaces/folders/lists, ignored for 'all')",
    ] = None,
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of tasks to return (max: 50, default: 20)"] = 20,
    order_by: Annotated[TaskOrderBy | None, "Field to sort tasks by"] = None,
    should_sort_by_reverse: Annotated[
        bool, "Whether to sort in descending order (default: False)"
    ] = False,
    statuses: Annotated[list[str] | None, "List of status strings to filter by"] = None,
    include_closed: Annotated[bool, "Whether to include closed tasks (default: False)"] = False,
    due_date_gt: Annotated[
        str | None,
        "Due date greater than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
    due_date_lt: Annotated[
        str | None,
        "Due date less than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
    date_created_gt: Annotated[
        str | None,
        "Created date greater than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
    date_created_lt: Annotated[
        str | None,
        "Created date less than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
) -> Annotated[dict[str, Any], "Filtered tasks from the specified scope"]:
    """
    Get filtered tasks from ClickUp with advanced filtering options.

    This unified tool filters tasks at different organizational levels:

    Important: Use this tool when not interested in a specific task but a set of tasks from a
    specific scope
    or filtering criteria that does not include the task title(name).
    """
    validate_workspace_id_and_raise(workspace_id)

    api_client = ClickupApiClient(context)
    request, norm_offset, norm_limit = _build_scoped_filter_params(
        scope=scope,
        item_ids=item_ids,
        offset=offset,
        limit=limit,
        order_by=order_by,
        should_sort_by_reverse=should_sort_by_reverse,
        statuses=statuses,
        include_closed=include_closed,
        due_date_gt=due_date_gt,
        due_date_lt=due_date_lt,
        date_created_gt=date_created_gt,
        date_created_lt=date_created_lt,
    )

    response = await execute_filtered_tasks_workflow(
        api_client=api_client,
        workspace_id=workspace_id,
        request=request,
        offset=norm_offset,
        limit=norm_limit,
        filter_context=scope.value,
    )

    return clean_dict(response)


@tool(requires_auth=ClickUp())
async def get_tasks_by_assignees(
    context: ToolContext,
    workspace_id: Annotated[
        str, "The ClickUp workspace ID for GUI URL generation (should be a number)"
    ],
    assignees_ids: Annotated[list[int], "List of assignee user IDs to get tasks for"],
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of tasks to return (max: 50, default: 20)"] = 20,
    order_by: Annotated[TaskOrderBy | None, "Field to sort tasks by"] = None,
    should_sort_by_reverse: Annotated[
        bool, "Whether to sort in descending order (default: False)"
    ] = False,
    statuses: Annotated[list[str] | None, "List of status strings to filter by"] = None,
    include_closed: Annotated[bool, "Whether to include closed tasks (default: False)"] = False,
    due_date_gt: Annotated[
        str | None,
        "Due date greater than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
    due_date_lt: Annotated[
        str | None,
        "Due date less than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
    date_created_gt: Annotated[
        str | None,
        "Created date greater than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
    date_created_lt: Annotated[
        str | None,
        "Created date less than (date string in format YYYY-MM-DD or YYYY-MM-DD HH:MM[:SS])",
    ] = None,
) -> Annotated[dict[str, Any], "Filtered tasks assigned to the specified assignees"]:
    """
    Get filtered tasks assigned to specific team members with advanced filtering options.

    This tool filters tasks by assignee(s) across the entire workspace.
    Provides comprehensive filtering capabilities including status and date range filtering.

    Important: Use this tool when not interested in a specific task but a set of tasks from
    a specific assignee
    or filtering criteria that does not include the task title(name).
    """
    api_client = ClickupApiClient(context)
    request, norm_offset, norm_limit = _build_assignees_filter_params(
        assignees_ids=assignees_ids,
        offset=offset,
        limit=limit,
        order_by=order_by,
        should_sort_by_reverse=should_sort_by_reverse,
        statuses=statuses,
        include_closed=include_closed,
        due_date_gt=due_date_gt,
        due_date_lt=due_date_lt,
        date_created_gt=date_created_gt,
        date_created_lt=date_created_lt,
    )

    response = await execute_filtered_tasks_workflow(
        api_client=api_client,
        workspace_id=workspace_id,
        request=request,
        offset=norm_offset,
        limit=norm_limit,
        filter_context="assignees",
    )

    return clean_dict(response)


@tool(requires_auth=ClickUp())
async def update_task_assignees(
    context: ToolContext,
    task_id: Annotated[str, "The ClickUp task ID to update assignees for"],
    assignee_ids_to_add: Annotated[list[int] | None, "List of user IDs to add as assignees"] = None,
    assignee_ids_to_remove: Annotated[
        list[int] | None, "List of user IDs to remove from assignees"
    ] = None,
) -> Annotated[dict[str, Any], "Result of the assignee update operation"]:
    """
    Update task assignees by adding and/or removing specific users.

    Use this tool to manage task assignments by specifying which users to add or remove.
    You can add assignees, remove assignees, or do both in a single operation.
    At least one of the parameters (assignee_ids_to_add or assignee_ids_to_remove) must be provided.
    """
    if not assignee_ids_to_add and not assignee_ids_to_remove:
        msg = (
            "No assignee operations specified. At least one of 'assignee_ids_to_add' or "
            "'assignee_ids_to_remove' must be provided."
        )
        raise ToolExecutionError(msg)

    api_client = ClickupApiClient(context)
    update_data = build_assignee_update_payload(
        assignee_ids_to_add=assignee_ids_to_add,
        assignee_ids_to_remove=assignee_ids_to_remove,
    )

    api_response = await api_client.update_task(task_id, update_data)

    result = map_task_assignee_update_to_tool_result(
        api_task=api_response,
        assignee_ids_to_add=assignee_ids_to_add,
        assignee_ids_to_remove=assignee_ids_to_remove,
    )
    return clean_dict(dict(result))


def _raise_no_teams_error() -> None:
    """Raise a standardized no teams found error."""
    msg = "No teams found for the authenticated user"
    raise ToolExecutionError(msg)
