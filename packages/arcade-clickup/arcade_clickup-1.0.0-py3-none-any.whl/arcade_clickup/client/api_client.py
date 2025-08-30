"""
ClickUp API client implementation.

This module provides a clean abstraction over HTTP operations for the ClickUp API.
"""

import asyncio
from dataclasses import dataclass
from typing import Any

import httpx
from arcade_tdk import ToolContext
from arcade_tdk.errors import ToolExecutionError

from arcade_clickup.constants import (
    CLICKUP_API_BASE_URL,
    CLICKUP_MAX_CONCURRENT_REQUESTS,
    CLICKUP_REQUEST_TIMEOUT,
    ERROR_MESSAGES,
)
from arcade_clickup.debug_tools.http_logging import get_http_event_hooks_if_enabled
from arcade_clickup.models.api_models import (
    ClickupWorkspace,
    CreateCommentReplyRequest,
    CreateCommentRequest,
    CreateTaskRequest,
    FilteredTeamTasksRequest,
    FilteredTeamTasksResponse,
    GetTaskCommentsResponse,
    GetThreadedCommentsResponse,
    UpdateCommentRequest,
    UpdateTaskRequest,
    WorkspacesResponse,
)


class ClickupApiError(ToolExecutionError):
    """Custom exception for ClickUp API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


@dataclass
class ClickupApiClient:
    """
    HTTP client abstraction for ClickUp API operations.

    This class encapsulates all HTTP communication with the ClickUp API,
    providing a clean interface for tools to use. It handles:
    - Authentication via API tokens
    - Request/response processing
    - Error handling and translation
    - Rate limiting through semaphores
    - Optional HTTP request/response logging via event hooks
    """

    context: ToolContext
    base_url: str = CLICKUP_API_BASE_URL
    max_concurrent_requests: int = CLICKUP_MAX_CONCURRENT_REQUESTS
    _semaphore: asyncio.Semaphore | None = None

    def __post_init__(self) -> None:
        """Initialize the semaphore for rate limiting."""
        if not self._semaphore:
            cached_semaphore = getattr(self.context, "_global_clickup_client_semaphore", None)
            if cached_semaphore:
                self._semaphore = cached_semaphore
            else:
                self._semaphore = asyncio.Semaphore(self.max_concurrent_requests)
                self.context._global_clickup_client_semaphore = self._semaphore  # type: ignore[attr-defined]
        self.base_url = self.base_url.rstrip("/")

    @property
    def _auth_token(self) -> str:
        """Get the authentication token from context."""
        token = self.context.get_auth_token_or_empty()
        if not token:
            raise ClickupApiError(ERROR_MESSAGES["no_auth_token"])
        return token

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers for ClickUp API requests."""
        return {
            "Authorization": self._auth_token,
            "Content-Type": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for API endpoint."""
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def _parse_error_response(self, response: httpx.Response) -> tuple[str, dict[str, Any] | None]:
        try:
            data = response.json()
        except Exception as e:
            return ERROR_MESSAGES["json_parse_error"].format(error=e), None

        # Common ClickUp error format includes 'err'/'ECODE'
        message = data.get("err", data.get("message", "Error"))
        return message, data

    async def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """Handle HTTP response and extract JSON data."""
        if response.status_code < 300:
            try:
                json_data = response.json()
                return json_data if isinstance(json_data, dict) else {}
            except Exception as e:
                raise ClickupApiError(ERROR_MESSAGES["json_parse_error"].format(error=e)) from e
        error_message, error_data = self._parse_error_response(response)
        raise ClickupApiError(
            error_message, status_code=response.status_code, response_data=error_data
        )

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make HTTP request to ClickUp API with proper error handling."""
        url = self._build_url(endpoint)
        headers = self._build_headers()

        # Configure httpx event hooks if logging is enabled
        event_hooks = get_http_event_hooks_if_enabled()

        if self._semaphore is None:
            msg = "Semaphore not initialized"
            raise ClickupApiError(msg)

        async with (
            self._semaphore,
            httpx.AsyncClient(event_hooks=event_hooks) as client,
        ):
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=CLICKUP_REQUEST_TIMEOUT,
                )

                result = await self._handle_response(response)
            except httpx.RequestError as e:
                raise ClickupApiError(ERROR_MESSAGES["request_failed"].format(error=e)) from e

            else:
                return result

    # Public API methods for specific operations

    async def get_user(self) -> dict[str, Any]:
        """
        Get the authenticated user's profile information.

        Returns:
            dict: User profile data
        """
        data = await self._make_request("GET", "/user")
        return data

    async def get_authorized_workspaces(self) -> WorkspacesResponse:
        """
        Get all workspaces (teams) the user has access to.

        Returns:
            WorkspacesResponse: List of authorized workspaces
        """
        data = await self._make_request("GET", "/team")
        return WorkspacesResponse(teams=data.get("teams", []))

    async def get_workspace_details(self, workspace_id: str) -> ClickupWorkspace:
        """
        Get detailed information about a specific workspace, including members.

        Args:
            workspace_id: The ID of the workspace

        Returns:
            ClickupWorkspace: Detailed workspace information including members
        """
        endpoint = f"/team/{workspace_id}"
        data = await self._make_request("GET", endpoint)
        return data.get("team", {})

    async def get_spaces(self, workspace_id: str, include_archived: bool = False) -> dict[str, Any]:
        """
        Get spaces from a workspace.

        Args:
            workspace_id: The ID of the workspace
            include_archived: Whether to include archived spaces

        Returns:
            dict: Response containing spaces data
        """
        endpoint = f"/team/{workspace_id}/space"
        params = {}
        if include_archived:
            params["archived"] = "true"

        data = await self._make_request("GET", endpoint, params=params)
        return data

    async def get_folders(self, space_id: str, include_archived: bool = False) -> dict[str, Any]:
        """
        Get folders from a space.

        Args:
            space_id: The ID of the space
            include_archived: Whether to include archived folders

        Returns:
            dict: Response containing folders data
        """
        endpoint = f"/space/{space_id}/folder"
        params = {}
        if include_archived:
            params["archived"] = "true"

        data = await self._make_request("GET", endpoint, params=params)
        return data

    async def get_lists(self, folder_id: str, include_archived: bool = False) -> dict[str, Any]:
        """
        Get lists from a folder.

        Args:
            folder_id: The ID of the folder
            include_archived: Whether to include archived lists

        Returns:
            dict: Response containing lists data
        """
        endpoint = f"/folder/{folder_id}/list"
        params = {}
        if include_archived:
            params["archived"] = "true"

        data = await self._make_request("GET", endpoint, params=params)
        return data

    async def get_list_details(self, list_id: str) -> dict[str, Any]:
        """
        Get details for a specific list, including its configured statuses.

        Args:
            list_id: The ID of the list

        Returns:
            dict: List details as returned by ClickUp (includes statuses, etc.)
        """
        endpoint = f"/list/{list_id}"
        data = await self._make_request("GET", endpoint)
        return data

    async def get_lists_from_space(self, space_id: str, archived: bool = False) -> dict[str, Any]:
        """
        Get all lists from a space.

        Args:
            space_id: The ID of the space
            archived: Whether to include archived lists

        Returns:
            dict: Response containing lists data
        """
        endpoint = f"/space/{space_id}/list"
        params = {"archived": str(archived).lower()}
        data = await self._make_request("GET", endpoint, params=params)
        return data

    async def get_task_by_id(
        self,
        task_id: str,
        include_subtasks: bool = False,
        custom_task_ids: bool = False,
        team_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get details for a specific task by ID.

        Args:
            task_id: The task ID or custom task ID
            include_subtasks: Whether to include subtasks
            custom_task_ids: Whether task_id is a custom ID
            team_id: Required if using custom_task_ids

        Returns:
            dict: Response containing task details
        """
        params = {"include_subtasks": str(include_subtasks).lower()}

        if custom_task_ids:
            if not team_id:
                msg = "team_id is required when using custom_task_ids"
                raise ValueError(msg)
            params["custom_task_ids"] = "true"
            endpoint = f"/team/{team_id}/task/{task_id}"
        else:
            endpoint = f"/task/{task_id}"

        data = await self._make_request("GET", endpoint, params=params)
        return data

    async def get_team_tasks_for_fuzzy_search(
        self, workspace_id: str, page: int = 0, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Get team tasks for fuzzy search with simplified parameters.

        Args:
            workspace_id: The workspace/team ID
            page: Page number (0-based)
            filters: Optional filters dict

        Returns:
            dict: Response containing tasks
        """
        endpoint = f"/team/{workspace_id}/task"

        params: dict[str, Any] = {
            "page": str(page),
            "order_by": "updated",
            "reverse": "false",  # Get most recent first
            "subtasks": "false",
        }

        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    params[f"{key}[]"] = value
                else:
                    params[key] = value

        data = await self._make_request("GET", endpoint, params=params)
        return data

    async def create_task(self, list_id: str, task_data: CreateTaskRequest) -> dict[str, Any]:
        """
        Create a new task in a ClickUp list.

        Args:
            list_id: The ID of the list where the task will be created
            task_data: Dictionary containing task information

        Returns:
            dict: The created task data
        """
        endpoint = f"/list/{list_id}/task"
        data = await self._make_request("POST", endpoint, json_data=dict(task_data))
        return data

    async def update_task(self, task_id: str, task_data: UpdateTaskRequest) -> dict[str, Any]:
        """
        Update an existing ClickUp task.

        Args:
            task_id: The ID of the task to update
            task_data: Dictionary containing updated task information

        Returns:
            dict: The updated task data
        """
        endpoint = f"/task/{task_id}"
        data = await self._make_request("PUT", endpoint, json_data=dict(task_data))
        return data

    async def get_filtered_team_tasks(
        self,
        workspace_id: str,
        request: FilteredTeamTasksRequest,
        offset: int = 0,
        limit: int = 50,
    ) -> FilteredTeamTasksResponse:
        """
        Get filtered team tasks using the ClickUp API.

        This method translates offset-based pagination to ClickUp's page-based system.
        ClickUp API uses page (0-based) with max 100 items per page.

        Args:
            workspace_id: The ID of the workspace/team
            request: Typed request parameters for filtering
            offset: Starting position (converted to page)
            limit: Number of items to return (max 100)

        Returns:
            FilteredTeamTasksResponse: Response containing tasks
        """
        endpoint = f"/team/{workspace_id}/task"

        limit = min(limit, 100)  # ClickUp max is 100

        # Calculate page number (ClickUp pages are 0-based)
        page = offset // 100

        params: dict[str, Any] = {}

        # Copy request parameters, handling arrays specially
        for key, value in request.items():
            if isinstance(value, list):
                # For array parameters, we need to format them as repeated parameters
                # ClickUp expects: assignees[]=123&assignees[]=456
                params[f"{key}[]"] = value
            else:
                params[key] = value

        params["page"] = page

        data = await self._make_request("GET", endpoint, params=params)

        original_tasks = data.get("tasks", [])
        total_tasks = len(original_tasks)

        # Calculate page offset within ClickUp's 100-item pages
        page_offset = offset % 100

        # Get tasks after applying page offset
        tasks_after_offset = original_tasks
        if page_offset > 0 and total_tasks > page_offset:
            tasks_after_offset = original_tasks[page_offset:]

        # Apply user's limit
        final_tasks = tasks_after_offset
        if len(final_tasks) > limit:
            final_tasks = final_tasks[:limit]

        # Determine if this is the last page for the TOOL (not ClickUp API)
        # We need to check if there would be more data available for the next tool request
        is_last_page = self._determine_is_last_page(
            original_tasks_count=total_tasks,
            tasks_after_offset_count=len(tasks_after_offset),
            final_tasks_count=len(final_tasks),
            requested_limit=limit,
            current_offset=offset,
            page_offset=page_offset,
        )

        return FilteredTeamTasksResponse(
            tasks=final_tasks,
            is_last_page=is_last_page,
        )

    def _determine_is_last_page(
        self,
        original_tasks_count: int,
        tasks_after_offset_count: int,
        final_tasks_count: int,
        requested_limit: int,
        current_offset: int,
        page_offset: int,
    ) -> bool:
        """
        Determine if this is the last page for the tool's pagination.

        This is complex because we need to account for:
        1. ClickUp's 100-item page limit
        2. User's requested limit (≤50)
        3. Offset within ClickUp pages
        4. Whether more data exists beyond current ClickUp page

        Args:
            original_tasks_count: Number of tasks returned by ClickUp API (≤100)
            tasks_after_offset_count: Tasks available after applying page offset
            final_tasks_count: Tasks actually returned to user
            requested_limit: User's requested limit
            current_offset: Current offset in tool pagination
            page_offset: Offset within ClickUp's 100-item page

        Returns:
            True if this is the last page for the tool
        """
        # Case 1: We got fewer tasks than requested → definitely last page
        if final_tasks_count < requested_limit:
            return True

        # Case 2: ClickUp returned less than 100 items → no more data in ClickUp
        if original_tasks_count < 100:
            # Check if we've consumed all available data
            return tasks_after_offset_count <= requested_limit

        # Case 3: ClickUp returned exactly 100 items → more data might exist
        # We need to check if the next request would have data
        if original_tasks_count == 100:
            # If we returned exactly what was requested and we're not at the end
            # of the ClickUp page, there's definitely more data
            remaining_in_clickup_page = original_tasks_count - page_offset
            if remaining_in_clickup_page > requested_limit:
                # More data exists in current ClickUp page
                return False
            else:
                # We consumed most/all of current ClickUp page
                # More data likely exists in next ClickUp page
                return False

        # Default: assume more data exists
        return False

    async def get_task_comments(
        self,
        task_id: str,
        start_id: str | None = None,
        start_ts: int | None = None,
    ) -> GetTaskCommentsResponse:
        """
        Get comments for a specific task.

        Args:
            task_id: The ID of the task
            start_id: Comment ID to start from (for pagination)
            start_ts: Timestamp to start from (for pagination)

        Returns:
            GetTaskCommentsResponse: Response containing comments
        """
        endpoint = f"/task/{task_id}/comment"
        params = {}
        if start_id:
            params["start_id"] = start_id
        if start_ts:
            params["start_ts"] = str(start_ts)

        data = await self._make_request("GET", endpoint, params=params)
        return data  # type: ignore[return-value]

    async def create_comment(
        self, task_id: str, comment_data: CreateCommentRequest
    ) -> dict[str, Any]:
        """
        Create a new comment on a task.

        Args:
            task_id: The ID of the task
            comment_data: Dictionary containing comment information

        Returns:
            dict: The created comment data
        """
        endpoint = f"/task/{task_id}/comment"
        data = await self._make_request("POST", endpoint, json_data=dict(comment_data))
        return data

    async def update_comment(
        self, comment_id: str, comment_data: UpdateCommentRequest
    ) -> dict[str, Any]:
        """
        Update an existing comment.

        Args:
            comment_id: The ID of the comment to update
            comment_data: Dictionary containing updated comment information

        Returns:
            dict: The updated comment data
        """
        endpoint = f"/comment/{comment_id}"
        data = await self._make_request("PUT", endpoint, json_data=dict(comment_data))
        return data

    async def get_comment_replies(self, comment_id: str) -> GetThreadedCommentsResponse:
        """
        Get threaded comments (replies) for a specific comment.

        Args:
            comment_id: The ID of the parent comment

        Returns:
            GetThreadedCommentsResponse: Response containing reply comments
        """
        endpoint = f"/comment/{comment_id}/reply"
        data = await self._make_request("GET", endpoint)
        return data  # type: ignore[return-value]

    async def create_comment_reply(
        self, comment_id: str, reply_data: CreateCommentReplyRequest
    ) -> dict[str, Any]:
        """
        Create a new reply to an existing comment.

        Args:
            comment_id: The ID of the parent comment
            reply_data: Dictionary containing reply information

        Returns:
            dict: The created reply comment data
        """
        endpoint = f"/comment/{comment_id}/reply"
        data = await self._make_request("POST", endpoint, json_data=dict(reply_data))
        return data
