"""
Helper functions for ClickUp comment operations.

This module provides utility functions for building payloads and processing
comment-related data for ClickUp API operations.
"""

from datetime import datetime, timezone
from typing import Any

from arcade_clickup.constants import CommentResolution
from arcade_clickup.models.api_models import (
    ClickupComment,
    CreateCommentReplyRequest,
    CreateCommentRequest,
    UpdateCommentRequest,
)
from arcade_clickup.models.tool_models import (
    CreateCommentReplyResult,
    CreateCommentResult,
    GetCommentRepliesResult,
    GetTaskCommentsResult,
    ToolComment,
    UpdateCommentResult,
)


def build_create_comment_payload(
    comment_text: str,
    assignee_id: int | None = None,
    notify_all: bool = True,
) -> CreateCommentRequest:
    """
    Build payload for creating a comment.

    Args:
        comment_text: The text content of the comment
        assignee_id: Optional user ID to assign the comment to
        notify_all: Whether to notify all task watchers

    Returns:
        CreateCommentRequest: Typed payload for ClickUp API
    """
    payload: CreateCommentRequest = {
        "comment_text": comment_text,
        "notify_all": notify_all,
    }

    if assignee_id is not None:
        payload["assignee"] = assignee_id

    return payload


def build_update_comment_payload(
    comment_text: str | None = None,
    assignee_id: int | None = None,
    resolution: CommentResolution | None = None,
) -> UpdateCommentRequest:
    """
    Build payload for updating a comment.

    Args:
        comment_text: Optional new text content for the comment
        assignee_id: Optional user ID to assign the comment to
        resolution: Optional resolution status for the comment

    Returns:
        UpdateCommentRequest: Typed payload for ClickUp API
    """
    payload: UpdateCommentRequest = {}

    if comment_text is not None:
        payload["comment_text"] = comment_text

    if assignee_id is not None:
        payload["assignee"] = assignee_id

    if resolution is not None:
        payload["resolved"] = resolution == CommentResolution.SET_AS_RESOLVED

    return payload


def map_comment_to_tool_model(api_comment: ClickupComment) -> ToolComment:
    """
    Convert ClickUp API comment model to simplified tool model.

    Args:
        api_comment: Raw comment data from ClickUp API

    Returns:
        ToolComment: Simplified comment data for tool output
    """
    tool_comment: ToolComment = {  # type: ignore[typeddict-item]
        "id": api_comment.get("id", ""),
        "text": api_comment.get("comment_text", api_comment.get("comment", "")),
        "user_id": str(api_comment.get("user", {}).get("id", "")),
        "user_name": api_comment.get("user", {}).get("username", "Unknown User"),
    }

    if "resolved" in api_comment:
        tool_comment["resolved"] = api_comment["resolved"]

    if "date" in api_comment:
        tool_comment["date"] = _format_comment_date(api_comment["date"])

    if "reply_count" in api_comment:
        tool_comment["reply_count"] = api_comment["reply_count"]

    # Add assignee information if present
    assignee = api_comment.get("assignee")
    if isinstance(assignee, dict):
        assignee_id = assignee.get("id")
        if assignee_id:
            tool_comment["assignee_id"] = str(assignee_id)
            tool_comment["assignee_name"] = assignee.get("username", "Unknown User")
        else:
            # Handle empty assignee dict
            tool_comment["assignee_id"] = ""
            tool_comment["assignee_name"] = "Unknown User"

    # Add assigned_by information if present
    assigned_by = api_comment.get("assigned_by")
    if isinstance(assigned_by, dict):
        assigned_by_id = assigned_by.get("id")
        if assigned_by_id:
            tool_comment["assigned_by_id"] = str(assigned_by_id)
            tool_comment["assigned_by_name"] = assigned_by.get("username", "Unknown User")
        else:
            # Handle empty assigned_by dict
            tool_comment["assigned_by_id"] = ""
            tool_comment["assigned_by_name"] = "Unknown User"

    return tool_comment


def create_get_comments_result(
    task_id: str,
    api_comments: list[ClickupComment],
    oldest_comment_id: str | None = None,
    is_last_page: bool = False,
) -> GetTaskCommentsResult:
    """
    Create GetTaskCommentsResult from API response.

    Args:
        task_id: The task ID comments belong to
        api_comments: Raw comment data from ClickUp API
        oldest_comment_id: ID of the oldest comment for pagination
        is_last_page: Whether this is the last page of comments

    Returns:
        GetTaskCommentsResult: Typed result for get_task_comments tool
    """
    tool_comments = [map_comment_to_tool_model(comment) for comment in api_comments]

    result: GetTaskCommentsResult = {  # type: ignore[typeddict-item]
        "success": True,
        "task_id": task_id,
        "comments": tool_comments,
        "total_comments": len(tool_comments),
        "message": f"{len(tool_comments)} comment{'s' if len(tool_comments) != 1 else ''}",
    }

    if is_last_page:
        # Don't include oldest_comment_id for last page
        pass
    elif oldest_comment_id:
        result["oldest_comment_id"] = oldest_comment_id

    return result


def create_comment_creation_result(
    task_id: str, api_comment: dict[str, Any]
) -> CreateCommentResult:
    """
    Create CreateCommentResult from API response.

    Args:
        task_id: The task ID the comment was created on
        api_comment: Raw comment data from ClickUp API

    Returns:
        CreateCommentResult: Typed result for create_comment tool
    """
    tool_comment = map_comment_to_tool_model(api_comment)  # type: ignore[arg-type]

    return {  # type: ignore[typeddict-item]
        "success": True,
        "comment": tool_comment,
        "task_id": task_id,
        "message": "Comment created",
    }


def create_comment_update_result(task_id: str, api_comment: dict[str, Any]) -> UpdateCommentResult:
    """
    Create UpdateCommentResult from API response.

    Args:
        task_id: The task ID the comment belongs to
        api_comment: Raw comment data from ClickUp API

    Returns:
        UpdateCommentResult: Typed result for update_comment tool
    """
    tool_comment = map_comment_to_tool_model(api_comment)  # type: ignore[arg-type]

    return {  # type: ignore[typeddict-item]
        "success": True,
        "comment": tool_comment,
        "task_id": task_id,
        "message": "Comment updated",
    }


# Private helpers (kept last)


def _format_comment_date(date_value: str | int) -> str:
    """
    Convert ClickUp comment date to human-readable format.

    ClickUp API returns dates as milliseconds since epoch (timestamp).
    This function converts them to ISO format with timezone info.

    Args:
        date_value: Date as string or int timestamp in milliseconds

    Returns:
        str: Human-readable date string in ISO format
    """
    try:
        timestamp_ms = int(date_value) if isinstance(date_value, str) else int(date_value)

        timestamp_s = timestamp_ms / 1000

        dt = datetime.fromtimestamp(timestamp_s, tz=timezone.utc)

        # Return ISO format string (e.g., "2025-01-15T10:30:45+00:00")
        return dt.isoformat()

    except (ValueError, TypeError):
        return str(date_value)


def build_create_comment_reply_payload(
    comment_text: str,
    assignee_id: int | None = None,
    notify_all: bool = True,
) -> CreateCommentReplyRequest:
    """
    Build payload for creating a comment reply.

    Args:
        comment_text: The text content of the reply
        assignee_id: Optional user ID to assign the reply to
        notify_all: Whether to notify all participants

    Returns:
        CreateCommentReplyRequest: Typed payload for ClickUp API
    """
    payload: CreateCommentReplyRequest = {
        "comment_text": comment_text,
        "notify_all": notify_all,
    }

    if assignee_id is not None:
        payload["assignee"] = assignee_id

    return payload


def create_get_replies_result(
    parent_comment_id: str,
    api_replies: list[ToolComment],
    items_returned: int | None = None,
    current_offset: int | None = None,
    next_offset: int | None = None,
    is_last: bool | None = None,
) -> GetCommentRepliesResult:
    """
    Create GetCommentRepliesResult from API response.

    Args:
        parent_comment_id: The parent comment ID
        api_replies: Mapped tool reply data
        items_returned: Number of items returned in this response (for pagination)
        current_offset: Current offset position (for pagination)
        next_offset: Next offset for pagination (for pagination)
        is_last: Whether this is the last page (for pagination)


    Returns:
        GetCommentRepliesResult: Typed result for get_comment_replies tool
    """
    final_is_last = is_last if is_last is not None else True

    result: GetCommentRepliesResult = {
        "success": True,
        "parent_comment_id": parent_comment_id,
        "replies": api_replies,
        "error": None,
        "message": f"{len(api_replies)} repl{'ies' if len(api_replies) != 1 else 'y'}",
        "items_returned": None,
        "current_offset": None,
        "next_offset": None,
        "is_last": final_is_last,
    }

    if not final_is_last:
        result["items_returned"] = (
            items_returned if items_returned is not None else len(api_replies)
        )
        result["current_offset"] = current_offset
        result["next_offset"] = next_offset

    return result


def create_comment_reply_result(
    parent_comment_id: str, api_reply: dict[str, Any]
) -> CreateCommentReplyResult:
    """
    Create CreateCommentReplyResult from API response.

    Args:
        parent_comment_id: The parent comment ID
        api_reply: Raw reply data from ClickUp API

    Returns:
        CreateCommentReplyResult: Typed result for create_comment_reply tool
    """
    tool_reply = map_comment_to_tool_model(api_reply)  # type: ignore[arg-type]

    return {  # type: ignore[typeddict-item]
        "success": True,
        "reply": tool_reply,
        "parent_comment_id": parent_comment_id,
        "message": "Reply created",
    }
