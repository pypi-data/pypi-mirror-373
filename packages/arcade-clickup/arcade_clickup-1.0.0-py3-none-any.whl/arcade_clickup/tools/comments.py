"""
Comment management tools for ClickUp.
"""

from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import ClickUp
from arcade_tdk.errors import ToolExecutionError

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.constants import CommentResolution
from arcade_clickup.utils.comment_helpers import (
    build_create_comment_payload,
    build_update_comment_payload,
    create_comment_creation_result,
    create_comment_update_result,
    create_get_comments_result,
)
from arcade_clickup.utils.helpers import clean_dict


@tool(requires_auth=ClickUp())
async def get_task_comments(
    context: ToolContext,
    task_id: Annotated[str, "The ClickUp task ID to get comments for"],
    limit: Annotated[int, "Number of comments to retrieve (max 25, default: 5)"] = 5,
    oldest_comment_id: Annotated[
        str | None, "ID of the oldest comment from previous call for pagination"
    ] = None,
) -> Annotated[dict[str, Any], "Comments for the specified task"]:
    """Get comments for a specific ClickUp task with pagination support.

    This tool retrieves comments from a task using ClickUp's specific pagination method.
    For the first call, omit oldest_comment_id. For subsequent calls, use the
    oldest_comment_id from the previous response to get the next set of comments.
    """
    if limit > 25:
        msg = "Limit cannot exceed 25 comments per request"
        raise ToolExecutionError(msg)
    if limit < 1:
        msg = "Limit must be at least 1"
        raise ToolExecutionError(msg)

    api_client = ClickupApiClient(context)
    api_response = await api_client.get_task_comments(
        task_id=task_id,
        start_id=oldest_comment_id,
    )

    comments = api_response.get("comments", [])

    limited_comments = comments[:limit]

    is_last_page = len(limited_comments) < limit

    next_oldest_id = None
    if limited_comments and not is_last_page:
        next_oldest_id = limited_comments[-1].get("id")

    result = create_get_comments_result(
        task_id=task_id,
        api_comments=limited_comments,
        oldest_comment_id=next_oldest_id,
        is_last_page=is_last_page,
    )
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def create_task_comment(
    context: ToolContext,
    task_id: Annotated[str, "The ClickUp task ID to add a comment to"],
    comment_text: Annotated[str, "The text content of the comment"],
    assignee_id: Annotated[int | None, "User ID to assign the comment to (optional)"] = None,
) -> Annotated[dict[str, Any], "Details of the created comment"]:
    """Create a new comment on a ClickUp task with optional assignment.

    Use this tool to add text comments to tasks. You can optionally assign
    the comment to a specific user for follow-up.
    """
    if not comment_text.strip():
        msg = "Comment text cannot be empty"
        raise ToolExecutionError(msg)

    api_client = ClickupApiClient(context)
    comment_data = build_create_comment_payload(
        comment_text=comment_text.strip(),
        assignee_id=assignee_id,
        notify_all=True,
    )

    api_response = await api_client.create_comment(task_id, comment_data)
    result = create_comment_creation_result(task_id, api_response)
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def update_task_comment(
    context: ToolContext,
    comment_id: Annotated[str, "The ClickUp comment ID to update"],
    task_id: Annotated[str, "The ClickUp task ID the comment belongs to"],
    comment_text: Annotated[str | None, "New text content for the comment (optional)"] = None,
    assignee_id: Annotated[int | None, "User ID to assign the comment to (optional)"] = None,
    resolution: Annotated[
        CommentResolution | None, "Set comment resolution status (optional)"
    ] = None,
) -> Annotated[dict[str, Any], "Details of the updated comment"]:
    """Update an existing comment on a ClickUp task.

    This tool is for updating top-level comments only, not threaded comment replies.
    Use this tool to modify comment text, change assignment, or set resolution status.
    At least one parameter (comment_text, assignee_id, or resolution) must be provided.
    """
    if comment_text is None and assignee_id is None and resolution is None:
        msg = "At least one of comment_text, assignee_id, or resolution must be provided"
        raise ToolExecutionError(msg)

    if comment_text is not None and not comment_text.strip():
        msg = "Comment text cannot be empty"
        raise ToolExecutionError(msg)

    api_client = ClickupApiClient(context)
    comment_data = build_update_comment_payload(
        comment_text=comment_text.strip() if comment_text else None,
        assignee_id=assignee_id,
        resolution=resolution,
    )

    api_response = await api_client.update_comment(comment_id, comment_data)
    result = create_comment_update_result(task_id, api_response)
    return clean_dict(dict(result))
