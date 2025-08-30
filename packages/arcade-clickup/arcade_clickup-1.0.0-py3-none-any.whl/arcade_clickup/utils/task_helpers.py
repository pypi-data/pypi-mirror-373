"""
Task-specific helper functions for ClickUp toolkit.
"""

from datetime import datetime, timezone
from typing import Any

from arcade_clickup.constants import CLICKUP_GUI_BASE_URL, TaskPriority
from arcade_clickup.models.api_models import CreateTaskRequest, UpdateTaskRequest
from arcade_clickup.models.tool_models import (
    CreateTaskResult,
    TaskAssignee,
    TaskAssigneeUpdateResult,
    ToolTask,
    UpdateTaskResult,
)


def build_create_task_payload(
    name: str,
    description: str = "",
    priority: TaskPriority | None = None,
    status: str | None = None,
    parent_task_id: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    points: int | None = None,
) -> CreateTaskRequest:
    payload: CreateTaskRequest = {
        "name": name,
        "description": description,
    }

    if priority is not None:
        payload["priority"] = _map_priority_to_int(priority)

    if status is not None:
        payload["status"] = status

    if parent_task_id is not None:
        payload["parent"] = parent_task_id

    if start_date is not None:
        epoch_ms, has_time = _parse_date_string_to_epoch_ms(start_date)
        payload["start_date"] = epoch_ms
        payload["start_date_time"] = has_time

    if due_date is not None:
        epoch_ms, has_time = _parse_date_string_to_epoch_ms(due_date)
        payload["due_date"] = epoch_ms
        payload["due_date_time"] = has_time

    if points is not None:
        payload["points"] = points

    return payload


def build_update_task_payload(
    name: str | None = None,
    description: str | None = None,
    priority: TaskPriority | None = None,
    status: str | None = None,
    parent_task_id: str | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    points: int | None = None,
) -> UpdateTaskRequest:
    payload: UpdateTaskRequest = {}

    if name is not None:
        payload["name"] = name

    if description is not None:
        payload["description"] = description

    if priority is not None:
        payload["priority"] = _map_priority_to_int(priority)

    if status is not None:
        payload["status"] = status

    if parent_task_id is not None:
        payload["parent"] = parent_task_id

    if start_date is not None:
        epoch_ms, has_time = _parse_date_string_to_epoch_ms(start_date)
        payload["start_date"] = epoch_ms
        payload["start_date_time"] = has_time

    if due_date is not None:
        epoch_ms, has_time = _parse_date_string_to_epoch_ms(due_date)
        payload["due_date"] = epoch_ms
        payload["due_date_time"] = has_time

    if points is not None:
        payload["points"] = points

    return payload


def build_assignee_update_payload(
    assignee_ids_to_add: list[int] | None = None,
    assignee_ids_to_remove: list[int] | None = None,
) -> UpdateTaskRequest:
    """
    Build payload for updating task assignees.

    Args:
        assignee_ids_to_add: List of user IDs to add as assignees
        assignee_ids_to_remove: List of user IDs to remove from assignees

    Returns:
        UpdateTaskRequest: Payload for the update task API
    """
    payload: UpdateTaskRequest = {}

    assignees_update: dict[str, list[int]] = {}

    if assignee_ids_to_add:
        assignees_update["add"] = assignee_ids_to_add

    if assignee_ids_to_remove:
        assignees_update["rem"] = assignee_ids_to_remove

    if assignees_update:
        payload["assignees"] = assignees_update

    return payload


def map_task_assignee_update_to_tool_result(
    api_task: dict[str, Any],
    assignee_ids_to_add: list[int] | None = None,
    assignee_ids_to_remove: list[int] | None = None,
) -> TaskAssigneeUpdateResult:
    """
    Map task assignee update API response to tool result.

    Args:
        api_task: Raw task data from ClickUp API after assignee update
        assignee_ids_to_add: List of user IDs that were added as assignees
        assignee_ids_to_remove: List of user IDs that were removed from assignees

    Returns:
        TaskAssigneeUpdateResult: Tool result with task info and operation summary
    """
    operations = _build_assignee_operations_summary(assignee_ids_to_add, assignee_ids_to_remove)
    operations_summary = _format_operations_summary(operations)

    task_id = api_task.get("id", "")
    result: TaskAssigneeUpdateResult = {
        "success": True,
        "task_id": task_id,
        "task_name": api_task.get("name", "Unknown Task"),
        "task_gui_url": api_task.get("url"),
        "assignees": None,  # TODO: This should be populated with actual assignee data
        "operations_summary": operations_summary,
        "message": "Assignees updated",
        "error": None,
    }

    if task_id:
        result["task_gui_url"] = f"{CLICKUP_GUI_BASE_URL}/t/{task_id}"
    else:
        if "task_gui_url" in result:
            del result["task_gui_url"]

    assignees = api_task.get("assignees")
    if assignees and isinstance(assignees, list):
        assignee_list = []
        for assignee in assignees:
            if isinstance(assignee, dict) and assignee.get("id"):
                assignee_obj: TaskAssignee = {
                    "id": str(assignee["id"]),
                    "name": assignee.get("username", assignee.get("email", "Unknown User")),
                }
                assignee_list.append(assignee_obj)
        if assignee_list:
            result["assignees"] = assignee_list

    return result


def create_task_creation_result(task: ToolTask, task_name: str) -> CreateTaskResult:
    """
    Create a CreateTaskResult for successful task creation.

    Args:
        task: The created task tool model
        task_name: The name of the created task

    Returns:
        CreateTaskResult: Tool result for task creation
    """
    result: CreateTaskResult = {
        "success": True,
        "task": task,
        "error": None,
        "message": "Task created",
    }
    return result


def _build_assignee_operations_summary(
    assignee_ids_to_add: list[int] | None,
    assignee_ids_to_remove: list[int] | None,
) -> list[str]:
    """Build list of operation descriptions."""
    operations = []

    if assignee_ids_to_add:
        count = len(assignee_ids_to_add)
        operations.append(f"added {count} assignee{'s' if count != 1 else ''}")

    if assignee_ids_to_remove:
        count = len(assignee_ids_to_remove)
        operations.append(f"removed {count} assignee{'s' if count != 1 else ''}")

    return operations


def _format_operations_summary(operations: list[str]) -> str:
    """Format operations list into summary string."""
    if not operations:
        return "no operations performed"
    elif len(operations) == 2:
        return f"{operations[0]} and {operations[1]}"
    else:
        return operations[0]


def _extract_current_assignees(assignees: list[dict]) -> dict[str, list[str]]:
    """Extract current assignee IDs and names."""
    current_assignee_ids = []
    current_assignee_names = []

    for assignee in assignees:
        if isinstance(assignee, dict):
            user_id = assignee.get("id")
            username = assignee.get("username", "")
            if user_id:
                current_assignee_ids.append(str(user_id))
                current_assignee_names.append(username or f"User {user_id}")

    return {"ids": current_assignee_ids, "names": current_assignee_names}


def create_task_update_result(
    task: ToolTask | None = None,
    task_id: str | None = None,
    error_message: str | None = None,
) -> UpdateTaskResult:
    """
    Create an UpdateTaskResult for task updates.

    Args:
        task: The updated task tool model (if successful)
        task_id: The task ID that was updated
        error_message: Error message if the update failed

    Returns:
        UpdateTaskResult: Tool result for task update
    """
    if error_message:
        error_result: UpdateTaskResult = {
            "success": False,
            "task": None,
            "error": error_message,
            "message": error_message,
        }
        return error_result

    if task and task_id:
        success_result: UpdateTaskResult = {
            "success": True,
            "task": task,
            "error": None,
            "message": "Task updated",
        }
        return success_result

    # Fallback case
    fallback_result: UpdateTaskResult = {
        "success": True,
        "task": None,
        "error": None,
        "message": "Task updated",
    }
    return fallback_result


# Private helpers (kept last)


def _parse_date_string_to_epoch_ms(date_str: str) -> tuple[int, bool]:
    """Parse a date string into epoch milliseconds and whether time was included."""
    normalized = date_str.strip()
    formats = (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
    )
    dt = None
    for fmt in formats:
        try:
            dt = datetime.strptime(normalized, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        try:
            dt = datetime.fromisoformat(normalized)
        except ValueError:
            try:
                val = int(normalized)
                if val > 10_000_000_000:
                    return val, True
                return val * 1000, True
            except Exception as e:
                msg = f"Invalid date string: {date_str}"
                raise ValueError(msg) from e

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    has_time = not (
        dt.hour == 0
        and dt.minute == 0
        and dt.second == 0
        and dt.microsecond == 0
        and ("T" not in normalized and " " not in normalized)
    )

    epoch_ms = int(dt.timestamp() * 1000)
    return epoch_ms, has_time


def _map_priority_to_int(priority: TaskPriority) -> int:
    """Map TaskPriority enum to ClickUp API integer priority."""
    mapping = {
        TaskPriority.URGENT: 1,
        TaskPriority.HIGH: 2,
        TaskPriority.NORMAL: 3,
        TaskPriority.LOW: 4,
    }
    return mapping[priority]
