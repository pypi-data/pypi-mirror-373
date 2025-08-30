"""
TypedDict models for ClickUp API responses.

These models represent the structure of data returned from ClickUp API endpoints.
They ensure type safety and provide clear documentation of expected response formats.
"""

from typing import Any, TypedDict

from typing_extensions import NotRequired


class ClickupUser(TypedDict):
    """User information from ClickUp API."""

    id: int
    username: str
    email: str
    color: str
    profilePicture: NotRequired[str]
    initials: str
    week_start_day: NotRequired[int]
    global_font_support: NotRequired[bool]
    timezone: NotRequired[str]
    custom_role: NotRequired[str]
    role: NotRequired[int]


class ClickupWorkspace(TypedDict):
    """Workspace (Team) information from ClickUp API."""

    id: str
    name: str
    color: str
    avatar: NotRequired[str]
    members: NotRequired[list[ClickupUser]]


class ClickupMember(TypedDict):
    """Member information for workspace members."""

    user: ClickupUser
    invited_by: NotRequired[ClickupUser]
    can_edit_tags: NotRequired[bool]
    can_see_time_spent: NotRequired[bool]
    can_see_time_estimated: NotRequired[bool]
    can_create_views: NotRequired[bool]
    custom_role: NotRequired[str]
    admin: NotRequired[bool]
    owner: NotRequired[bool]


class WorkspacesResponse(TypedDict):
    """Response from Get Authorized Workspaces endpoint."""

    teams: list[ClickupWorkspace]


class MembersResponse(TypedDict):
    """Response from Get Team Members endpoint."""

    members: list[ClickupMember]


class ClickupSpace(TypedDict):
    """Space information from ClickUp API."""

    id: str
    name: str
    color: NotRequired[str]
    private: NotRequired[bool]
    avatar: NotRequired[str]
    admin_can_manage: NotRequired[bool]
    statuses: NotRequired[list[dict]]
    multiple_assignees: NotRequired[bool]
    features: NotRequired[dict]
    archived: NotRequired[bool]


class ClickupFolder(TypedDict):
    """Folder information from ClickUp API."""

    id: str
    name: str
    orderindex: NotRequired[int]
    override_statuses: NotRequired[bool]
    hidden: NotRequired[bool]
    space: NotRequired[ClickupSpace]
    task_count: NotRequired[str]
    archived: NotRequired[bool]
    statuses: NotRequired[list[dict]]
    lists: NotRequired[list["ClickupList"]]


class ClickupList(TypedDict):
    """List information from ClickUp API."""

    id: str
    name: str
    orderindex: NotRequired[int]
    content: NotRequired[str]
    status: NotRequired[dict]
    priority: NotRequired[dict]
    assignee: NotRequired[ClickupUser]
    task_count: NotRequired[int]
    due_date: NotRequired[str]
    due_date_time: NotRequired[bool]
    start_date: NotRequired[str]
    start_date_time: NotRequired[bool]
    folder: NotRequired[ClickupFolder]
    space: NotRequired[ClickupSpace]
    inbound_address: NotRequired[str]
    archived: NotRequired[bool]
    override_statuses: NotRequired[bool]
    statuses: NotRequired[list[dict]]
    permission_level: NotRequired[str]


class SpacesResponse(TypedDict):
    """Response from Get Spaces endpoint."""

    spaces: list[ClickupSpace]


class FoldersResponse(TypedDict):
    """Response from Get Folders endpoint."""

    folders: list[ClickupFolder]


class ListsResponse(TypedDict):
    """Response from Get Lists endpoint."""

    lists: list[ClickupList]


class ClickupTask(TypedDict):
    """Task information from ClickUp API."""

    id: str
    name: str
    description: NotRequired[str]
    status: NotRequired[dict]
    orderindex: NotRequired[str]
    date_created: NotRequired[str]
    date_updated: NotRequired[str]
    date_closed: NotRequired[str]
    creator: NotRequired[ClickupUser]
    assignees: NotRequired[list[ClickupUser]]
    watchers: NotRequired[list[ClickupUser]]
    checklists: NotRequired[list[dict]]
    parent: NotRequired[str]
    priority: NotRequired[dict]
    due_date: NotRequired[str]
    start_date: NotRequired[str]
    points: NotRequired[int]
    time_estimate: NotRequired[int]
    time_spent: NotRequired[int]
    custom_fields: NotRequired[list[dict]]
    dependencies: NotRequired[list[dict]]
    linked_tasks: NotRequired[list[dict]]
    list: NotRequired[ClickupList]
    folder: NotRequired[ClickupFolder]
    space: NotRequired[ClickupSpace]
    project: NotRequired[dict]
    url: NotRequired[str]


class CreateTaskRequest(TypedDict):
    """Request payload for creating a task."""

    name: str
    description: NotRequired[str]
    status: NotRequired[str]
    priority: NotRequired[int]
    due_date: NotRequired[int]
    due_date_time: NotRequired[bool]
    start_date: NotRequired[int]
    start_date_time: NotRequired[bool]
    parent: NotRequired[str]
    points: NotRequired[int]
    custom_fields: NotRequired[list[dict[str, Any]]]


class UpdateTaskRequest(TypedDict):
    """Request payload for updating a task."""

    name: NotRequired[str]
    description: NotRequired[str]
    status: NotRequired[str]
    priority: NotRequired[int]
    due_date: NotRequired[int]
    due_date_time: NotRequired[bool]
    start_date: NotRequired[int]
    start_date_time: NotRequired[bool]
    parent: NotRequired[str]
    points: NotRequired[int]
    assignees: NotRequired[dict[str, list[int]]]
    custom_fields: NotRequired[list[dict[str, Any]]]


class FilteredTeamTasksRequest(TypedDict):
    """Request parameters for Get Filtered Team Tasks endpoint."""

    page: NotRequired[int]
    order_by: NotRequired[str]
    reverse: NotRequired[str]
    statuses: NotRequired[list[str]]
    include_closed: NotRequired[str]
    assignees: NotRequired[list[int]]
    space_ids: NotRequired[list[str]]
    folder_ids: NotRequired[list[str]]
    list_ids: NotRequired[list[str]]
    due_date_gt: NotRequired[int]
    due_date_lt: NotRequired[int]
    date_created_gt: NotRequired[int]
    date_created_lt: NotRequired[int]


class FilteredTeamTasksResponse(TypedDict):
    """Response from Get Filtered Team Tasks endpoint."""

    tasks: list[ClickupTask]
    is_last_page: NotRequired[bool]  # Whether this is the last page of results


class ClickupComment(TypedDict):
    """Comment information from ClickUp API."""

    id: str
    comment: str
    comment_text: str
    user: ClickupUser
    resolved: NotRequired[bool]
    assignee: NotRequired[ClickupUser]
    assigned_by: NotRequired[ClickupUser]
    reactions: NotRequired[list[dict[str, Any]]]
    date: NotRequired[str]
    reply_count: NotRequired[int]


class CreateCommentRequest(TypedDict):
    """Request payload for creating a comment."""

    comment_text: str
    assignee: NotRequired[int]
    notify_all: NotRequired[bool]


class UpdateCommentRequest(TypedDict):
    """Request payload for updating a comment."""

    comment_text: NotRequired[str]
    assignee: NotRequired[int]
    resolved: NotRequired[bool]


class GetTaskCommentsResponse(TypedDict):
    """Response from Get Task Comments endpoint."""

    comments: list[ClickupComment]


class CreateCommentReplyRequest(TypedDict):
    """Request payload for creating a threaded comment reply."""

    comment_text: str
    assignee: NotRequired[int]
    notify_all: NotRequired[bool]


class GetThreadedCommentsResponse(TypedDict):
    """Response from Get Threaded Comments endpoint."""

    comments: list[ClickupComment]
