"""
Helper functions for ClickUp tools.

This module contains utility functions that are used across multiple tools
for common operations like validation, formatting, and data processing.
"""

import asyncio
from typing import Any, cast

from arcade_tdk.errors import ToolExecutionError

from arcade_clickup.client.api_client import ClickupApiClient, ClickupApiError
from arcade_clickup.constants import (
    CLICKUP_GUI_BASE_URL,
    DEVELOPER_ERROR_MESSAGES,
    ERROR_MESSAGES,
    ROLE_MAPPING,
    STATUS_CODE_MESSAGES,
)
from arcade_clickup.models.api_models import (
    ClickupFolder,
    ClickupList,
    ClickupMember,
    ClickupSpace,
    ClickupTask,
    ClickupWorkspace,
)
from arcade_clickup.models.tool_models import (
    GetPossibleStatusesToolResult,
    ShortWorkspace,
    ToolFolder,
    ToolList,
    ToolListStatus,
    ToolMember,
    ToolSpace,
    ToolTask,
    ToolWorkspace,
)


def validate_workspace_id(workspace_id: str) -> bool:
    """
    Validate a ClickUp workspace ID format.

    Args:
        workspace_id: The workspace ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not workspace_id or not isinstance(workspace_id, str):
        return False

    return workspace_id.isdigit() and len(workspace_id) > 0


def validate_workspace_id_and_raise(workspace_id: str) -> None:
    """
    Validate a ClickUp workspace ID format and raise ToolExecutionError if invalid.

    Args:
        workspace_id: The workspace ID to validate

    Raises:
        ToolExecutionError: If the workspace ID is invalid
    """
    if not validate_workspace_id(workspace_id):
        message = f"Invalid workspace ID '{workspace_id}'. It should be a number."
        developer_message = f"Workspace validation failed for ID '{workspace_id}'"
        raise ToolExecutionError(message=message, developer_message=developer_message)


def format_api_error(error: ClickupApiError) -> str:
    """
    Format a ClickupApiError into a user-friendly error message.

    Args:
        error: The ClickupApiError to format

    Returns:
        str: Formatted error message
    """
    base_message = str(error)

    if error.status_code:
        # Check for specific status codes first
        if error.status_code in STATUS_CODE_MESSAGES:
            return STATUS_CODE_MESSAGES[error.status_code]
        elif error.status_code >= 500:
            return STATUS_CODE_MESSAGES[500]

    return f"ClickUp API error: {base_message}"


def map_workspace_to_tool_model(api_workspace: ClickupWorkspace) -> ToolWorkspace:
    """
    Convert API workspace model to simplified tool model.

    Args:
        api_workspace: Raw workspace data from ClickUp API

    Returns:
        ToolWorkspace: Simplified workspace data for tool output
    """
    tool_workspace: ToolWorkspace = {
        "id": api_workspace["id"],
        "name": api_workspace["name"],
        "color": api_workspace["color"],
        "avatar": api_workspace.get("avatar"),
        "member_count": len(api_workspace["members"])
        if "members" in api_workspace
        else api_workspace.get("member_count"),  # type: ignore[typeddict-item]
        "gui_url": f"{CLICKUP_GUI_BASE_URL}/{api_workspace['id']}",
    }

    return tool_workspace


def map_workspace_to_short_model(api_workspace: ClickupWorkspace) -> ShortWorkspace:
    """
    Convert API workspace model to a short model with only id and name.

    Args:
        api_workspace: Raw workspace data from ClickUp API

    Returns:
        ShortWorkspace: Minimal workspace data for summary outputs
    """
    return ShortWorkspace(
        id=str(api_workspace.get("id", "")),
        name=str(api_workspace.get("name", "")),
    )


def map_member_to_tool_model(api_member: ClickupMember) -> ToolMember:
    """
    Convert API member model to simplified tool model.

    Args:
        api_member: Raw member data from ClickUp API

    Returns:
        ToolMember: Simplified member data for tool output
    """
    user = api_member.get("user", {})
    tool_member: ToolMember = {
        "id": user.get("id", 0),
        "name": user.get("username", "Unknown"),
        "email": user.get("email", ""),
        "initials": user.get("initials", ""),
        "avatar": user.get("profilePicture"),
        "role": None,  # Will be set below with proper logic
    }

    # Add role information from user object
    if user.get("custom_role"):
        tool_member["role"] = user["custom_role"]
    elif user.get("role"):
        # Map numeric role to string using constants
        role_id = user.get("role")
        if isinstance(role_id, int) and role_id in ROLE_MAPPING:
            tool_member["role"] = ROLE_MAPPING[role_id]
        else:
            tool_member["role"] = f"role_{role_id}"

    return tool_member


def map_space_to_tool_model(api_space: ClickupSpace, workspace_id: str | None = None) -> ToolSpace:
    """
    Convert ClickUp API space model to simplified tool model.

    Args:
        api_space: Raw space data from ClickUp API
        workspace_id: Optional workspace ID for constructing GUI URL

    Returns:
        ToolSpace: Simplified space data for tool output
    """
    tool_space: ToolSpace = {  # type: ignore[typeddict-item]
        "id": api_space.get("id", ""),
        "name": api_space.get("name", "Unknown Space"),
    }

    if api_space.get("color"):
        tool_space["color"] = api_space["color"]
    if api_space.get("private") is not None:
        tool_space["private"] = api_space["private"]
    if api_space.get("avatar"):
        tool_space["avatar"] = api_space["avatar"]
    if api_space.get("archived") is not None:
        tool_space["archived"] = api_space["archived"]

    if workspace_id:
        tool_space["gui_url"] = (
            f"{CLICKUP_GUI_BASE_URL}/{workspace_id}/v/o/s/{api_space.get('id', '')}"
        )

    return tool_space


def map_folder_to_tool_model(
    api_folder: ClickupFolder, workspace_id: str | None = None
) -> ToolFolder:
    """
    Convert ClickUp API folder model to simplified tool model.

    Args:
        api_folder: Raw folder data from ClickUp API
        workspace_id: Optional workspace ID for constructing GUI URL

    Returns:
        ToolFolder: Simplified folder data for tool output
    """
    tool_folder: ToolFolder = {  # type: ignore[typeddict-item]
        "id": api_folder.get("id", ""),
        "name": api_folder.get("name", "Unknown Folder"),
    }

    if api_folder.get("task_count"):
        tool_folder["task_count"] = api_folder["task_count"]
    if api_folder.get("archived") is not None:
        tool_folder["archived"] = api_folder["archived"]
    if api_folder.get("hidden") is not None:
        tool_folder["hidden"] = api_folder["hidden"]

    space = api_folder.get("space")
    if space:
        tool_folder["space_id"] = space.get("id", "")
        tool_folder["space_name"] = space.get("name", "")

    if workspace_id:
        folder_id = api_folder.get("id", "")
        tool_folder["gui_url"] = f"{CLICKUP_GUI_BASE_URL}/{workspace_id}/v/o/f/{folder_id}"

    return tool_folder


def map_list_to_tool_model(api_list: ClickupList, workspace_id: str | None = None) -> ToolList:
    """
    Convert ClickUp API list model to simplified tool model.

    Args:
        api_list: Raw list data from ClickUp API
        workspace_id: Optional workspace ID for constructing GUI URL

    Returns:
        ToolList: Simplified list data for tool output
    """
    tool_list: ToolList = {  # type: ignore[typeddict-item]
        "id": api_list.get("id", ""),
        "name": api_list.get("name", "Unknown List"),
    }

    # Add optional list fields
    if api_list.get("task_count") is not None:
        tool_list["task_count"] = api_list["task_count"]
    if api_list.get("archived") is not None:
        tool_list["archived"] = api_list["archived"]
    if api_list.get("permission_level"):
        tool_list["permission_level"] = api_list["permission_level"]

    # Add folder information if available
    folder = api_list.get("folder")
    if folder:
        tool_list["folder_id"] = folder.get("id", "")
        tool_list["folder_name"] = folder.get("name", "")

    space = api_list.get("space")
    if space:
        tool_list["space_id"] = space.get("id", "")
        tool_list["space_name"] = space.get("name", "")

    if workspace_id:
        list_id = api_list.get("id", "")
        tool_list["gui_url"] = f"{CLICKUP_GUI_BASE_URL}/{workspace_id}/v/l/li/{list_id}"

    return tool_list


def map_task_to_tool_model(api_task: ClickupTask, workspace_id: str | None = None) -> ToolTask:
    """
    Convert ClickUp API task model to simplified tool model.

    Args:
        api_task: Raw task data from ClickUp API
        workspace_id: Optional workspace ID for constructing GUI URL

    Returns:
        ToolTask: Simplified task data for tool output
    """
    tool_task: ToolTask = {  # type: ignore[typeddict-item]
        "id": api_task.get("id", ""),
        "name": api_task.get("name", "Unknown Task"),
    }

    _set_task_description(tool_task, api_task)
    _set_task_status_and_priority(tool_task, api_task)
    _set_task_dates_and_points(tool_task, api_task)
    _set_task_relationships(tool_task, api_task)
    _set_task_urls(tool_task, api_task)

    return tool_task


def map_list_statuses_to_tool_model(raw_statuses: list[dict]) -> list[ToolListStatus]:
    """Convert raw list statuses from API to simplified tool model list.

    Args:
        raw_statuses: The list of status dicts from ClickUp list details

    Returns:
        list[ToolListStatus]: Normalized statuses with status, orderindex, type, color
    """
    result: list[ToolListStatus] = []
    for s in raw_statuses or []:
        label = s.get("status") or s.get("name")
        if not label:
            continue
        item: ToolListStatus = {
            "status": label,
            "orderindex": s.get("orderindex"),
            "type": s.get("type"),
            "color": s.get("color"),
        }
        result.append(item)
    return result


def clean_dict(data: dict) -> dict:
    """
    Clean a dictionary by removing None values recursively.

    Args:
        data: Dictionary to clean

    Returns:
        dict: New dictionary with None values removed
    """
    if not isinstance(data, dict):
        return data

    filtered: dict[str, Any] = {}
    for key, value in data.items():
        cleaned_value = _clean_value(value)
        if cleaned_value is not None:
            filtered[key] = cleaned_value

    return filtered


def create_possible_statuses_result(
    list_id: str, statuses: list[ToolListStatus]
) -> GetPossibleStatusesToolResult:
    """
    Create a result for get_statuses_for_list tool.

    Args:
        list_id: The list ID
        statuses: The list of statuses

    Returns:
        GetPossibleStatusesToolResult: Tool result for statuses
    """
    result: GetPossibleStatusesToolResult = {
        "success": True,
        "list_id": list_id,
        "statuses": statuses,
    }
    return result


def _clean_value(value: Any) -> Any:
    """Clean a single value (dict, list, or primitive)."""
    if value is None:
        return None
    elif isinstance(value, dict):
        cleaned_nested = clean_dict(value)
        return cleaned_nested if cleaned_nested else None
    elif isinstance(value, list):
        cleaned_list: list[Any] = []
        for item in value:
            if item is None:
                continue
            elif isinstance(item, dict):
                cleaned_item = clean_dict(item)
                if cleaned_item:
                    cleaned_list.append(cleaned_item)
            else:
                cleaned_list.append(item)
        # Return list if it has items or if original was empty list
        return cleaned_list if cleaned_list or value == [] else None
    else:
        return value


def _extract_assignee_ids(assignees: Any) -> list[str]:
    """Extract assignee IDs from assignees list."""
    if not assignees or not isinstance(assignees, list):
        return []

    assignee_ids = []
    for assignee in assignees:
        if isinstance(assignee, dict) and assignee.get("id"):
            assignee_ids.append(str(assignee["id"]))
    return assignee_ids


def _extract_list_info(list_info: Any) -> dict[str, Any]:
    """Extract list information from API response."""
    if not list_info or not isinstance(list_info, dict):
        return {}

    result = {}
    if list_info.get("id"):
        result["list_id"] = list_info["id"]
    if list_info.get("name"):
        result["list_name"] = list_info["name"]
    return result


def _set_task_description(tool_task: ToolTask, api_task: ClickupTask) -> None:
    """Set task description if available."""
    if api_task.get("description"):
        tool_task["description"] = api_task["description"]


def _set_task_status_and_priority(tool_task: ToolTask, api_task: ClickupTask) -> None:
    """Set task status and priority from API data."""
    status = api_task.get("status")
    if status and isinstance(status, dict):
        tool_task["status"] = status.get("status", "")

    priority = api_task.get("priority")
    if priority and isinstance(priority, dict):
        priority_id = priority.get("id")
        if priority_id:
            tool_task["priority"] = int(priority_id)


def _set_task_dates_and_points(tool_task: ToolTask, api_task: ClickupTask) -> None:
    """Set task dates, points, and parent information."""
    if api_task.get("parent"):
        tool_task["parent_id"] = api_task["parent"]

    if api_task.get("due_date"):
        tool_task["due_date"] = api_task["due_date"]
    if api_task.get("start_date"):
        tool_task["start_date"] = api_task["start_date"]

    if api_task.get("points") is not None:
        tool_task["points"] = api_task["points"]


def _set_task_relationships(tool_task: ToolTask, api_task: ClickupTask) -> None:
    """Set task relationships (assignees, list, folder, space)."""
    assignee_ids = _extract_assignee_ids(api_task.get("assignees"))
    if assignee_ids:
        tool_task["assignees"] = assignee_ids

    list_data = _extract_list_info(api_task.get("list"))
    if "list_id" in list_data:
        tool_task["list_id"] = list_data["list_id"]
    if "list_name" in list_data:
        tool_task["list_name"] = list_data["list_name"]

    folder = api_task.get("folder")
    if folder and isinstance(folder, dict):
        tool_task["folder_id"] = folder.get("id", "")
        tool_task["folder_name"] = folder.get("name", "")

    space = api_task.get("space")
    if space and isinstance(space, dict):
        tool_task["space_id"] = space.get("id", "")
        tool_task["space_name"] = space.get("name", "")


def _set_task_urls(tool_task: ToolTask, api_task: ClickupTask) -> None:
    """Set task URLs."""
    if api_task.get("url"):
        tool_task["url"] = api_task["url"]

    task_id = api_task.get("id", "")
    if task_id:
        simple_task_url = f"{CLICKUP_GUI_BASE_URL}/t/{task_id}"
        tool_task["task_gui_url"] = simple_task_url
        tool_task["gui_url"] = simple_task_url


async def execute_get_lists_for_space_workflow(
    api_client: ClickupApiClient,
    space_id: str,
    workspace_id: str,
    include_archived: bool = False,
) -> list[ToolList]:
    """
    Execute the workflow to get all lists from a space by collecting lists from all folders.

    This function handles the complex logic of:
    1. Getting all folders within the specified space
    2. Concurrently fetching lists from each folder
    3. Returning the aggregated list of tool models

    Args:
        api_client: ClickUp API client
        space_id: The ClickUp space ID to get lists from
        workspace_id: The ClickUp workspace ID for GUI URL generation
        include_archived: Whether to include archived lists

    Returns:
        list[ToolList]: List of tool models for all lists in the space
    """
    folders_response = await api_client.get_folders(
        space_id=space_id, include_archived=include_archived
    )

    raw_folders = folders_response.get("folders", [])

    async def get_lists_for_folder(folder: dict) -> list[ToolList]:
        folder_id = cast(str, folder.get("id"))
        lists_response = await api_client.get_lists(
            folder_id=folder_id, include_archived=include_archived
        )
        raw_lists = lists_response.get("lists", [])
        return [map_list_to_tool_model(list_item, workspace_id) for list_item in raw_lists]

    folder_tasks = [get_lists_for_folder(folder) for folder in raw_folders]
    folder_results = await asyncio.gather(*folder_tasks)

    all_lists = []
    for folder_lists in folder_results:
        all_lists.extend(folder_lists)

    return all_lists


def raise_workspace_not_found_error(workspace_id: str) -> None:
    """
    Raise a standardized workspace not found error.

    Args:
        workspace_id: The workspace ID that was not found

    Raises:
        ToolExecutionError: Standardized error with workspace not found message
    """
    message = ERROR_MESSAGES["workspace_not_found"].format(workspace_id=workspace_id)
    developer_message = DEVELOPER_ERROR_MESSAGES["workspace_not_found"].format(
        workspace_id=workspace_id
    )
    raise ToolExecutionError(message=message, developer_message=developer_message)
