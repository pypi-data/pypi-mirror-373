"""
Threaded comment management tools for ClickUp.

This module provides tools for managing comment replies and threaded conversations
in ClickUp tasks.
"""

from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import ClickUp
from arcade_tdk.errors import ToolExecutionError

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.utils.comment_helpers import (
    build_create_comment_reply_payload,
    create_comment_reply_result,
    create_get_replies_result,
    map_comment_to_tool_model,
)
from arcade_clickup.utils.helpers import clean_dict
from arcade_clickup.utils.offset_helper import OffsetHelper, OffsetParams


@tool(requires_auth=ClickUp())
async def get_task_comment_replies(
    context: ToolContext,
    comment_id: Annotated[str, "The ClickUp comment ID to get replies for"],
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of replies to return (max: 50, default: 20)"] = 20,
) -> Annotated[dict[str, Any], "Threaded replies for the specified comment"]:
    """Get threaded replies for a specific ClickUp comment with pagination support.

    This tool retrieves replies to a parent comment using ClickUp's threaded
    comment system with offset-based pagination. The parent comment itself
    is not included in the results, only the threaded replies.
    """
    offset_params = OffsetParams(offset=offset, limit=limit, max_limit=50)

    api_client = ClickupApiClient(context)
    api_response = await api_client.get_comment_replies(comment_id)
    replies = api_response.get("comments", [])

    all_replies = [map_comment_to_tool_model(reply) for reply in replies]

    offset_result = OffsetHelper.offset_and_sort(
        items=all_replies,
        offset_params=offset_params,
    )

    result = create_get_replies_result(
        parent_comment_id=comment_id,
        api_replies=offset_result.items,
        items_returned=offset_result.actual_returned,
        current_offset=offset_result.current_offset,
        next_offset=offset_result.next_offset,
        is_last=offset_result.is_last,
    )
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def create_task_comment_reply(
    context: ToolContext,
    comment_id: Annotated[str, "The ClickUp comment ID to reply to"],
    reply_text: Annotated[str, "The text content of the reply"],
    assignee_id: Annotated[int | None, "User ID to assign the reply to"] = None,
) -> Annotated[dict[str, Any], "Details of the created reply"]:
    """Create a new threaded reply to an existing ClickUp comment.

    Use this tool to add threaded replies to comments, creating conversation threads.
    You can optionally assign the reply to a specific user for follow-up.
    """
    if not reply_text.strip():
        msg = "Reply text cannot be empty"
        raise ToolExecutionError(msg)

    api_client = ClickupApiClient(context)
    reply_data = build_create_comment_reply_payload(
        comment_text=reply_text.strip(),
        assignee_id=assignee_id,
        notify_all=True,
    )

    api_response = await api_client.create_comment_reply(comment_id, reply_data)
    result = create_comment_reply_result(comment_id, api_response)
    return clean_dict(dict(result))
