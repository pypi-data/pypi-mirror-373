"""
TypedDict models for tool outputs and responses.

These models define the structure of data returned by our ClickUp tools.
They provide a clean, simplified interface for tool consumers, exposing only
the essential fields without internal API details.
"""

from typing import TypedDict

from typing_extensions import NotRequired


class ToolError(TypedDict):
    """Standard error structure for tool responses."""

    error: str
    error_code: str | None
    details: str | None


class ToolWorkspace(TypedDict):
    """Simplified workspace information for tool outputs."""

    id: str
    name: str
    color: str
    avatar: str | None
    member_count: int | None
    gui_url: str | None


class ToolMember(TypedDict):
    """Simplified member information for tool outputs."""

    id: int
    name: str
    email: str
    initials: str
    avatar: str | None
    role: str | None


class GetTeamMembersResult(TypedDict):
    """
    Result structure for get_team_members tool.

    Compatible with OffsetResponse protocol when offset fields are present.
    """

    success: bool
    workspace_id: str | None
    workspace_name: str | None
    members: list[ToolMember] | None
    count: int | None
    current_offset: int | None
    next_offset: int | None
    is_last: bool | None
    error: str | None
    message: str | None


class ToolSpace(TypedDict):
    """Simplified space information for tool outputs."""

    id: str
    name: str
    color: str | None
    private: bool | None
    avatar: str | None
    archived: bool | None
    gui_url: str | None


class ToolFolder(TypedDict):
    """Simplified folder information for tool outputs."""

    id: str
    name: str
    space_id: str | None
    space_name: str | None
    task_count: str | None
    archived: bool | None
    hidden: bool | None
    gui_url: str | None


class ToolList(TypedDict):
    """Simplified list information for tool outputs."""

    id: str
    name: str
    folder_id: str | None
    folder_name: str | None
    space_id: str | None
    space_name: str | None
    task_count: int | None
    archived: bool | None
    permission_level: str | None
    gui_url: str | None


class GetSpacesResult(TypedDict):
    """
    Result structure for get_spaces tool.

    Compatible with OffsetResponse protocol when offset fields are present.
    """

    success: bool
    workspace_id: str | None
    spaces: list[ToolSpace] | None
    count: int | None
    current_offset: int | None
    next_offset: int | None
    is_last: bool | None
    error: str | None
    message: str | None


class GetFoldersResult(TypedDict):
    """
    Result structure for get_folders tool.

    Compatible with OffsetResponse protocol when offset fields are present.
    """

    success: bool
    space_id: str | None
    folders: list[ToolFolder] | None
    count: int | None
    current_offset: int | None
    next_offset: int | None
    is_last: bool | None
    error: str | None
    message: str | None


class ToolTask(TypedDict):
    """Simplified task information for tool outputs."""

    id: str
    name: str
    description: str | None
    status: str | None
    priority: int | None
    assignees: list[str] | None
    tags: list[str] | None
    parent_id: str | None
    due_date: str | None
    start_date: str | None
    points: int | None
    list_id: str | None
    list_name: str | None
    folder_id: str | None
    folder_name: str | None
    space_id: str | None
    space_name: str | None
    url: str | None
    gui_url: str | None
    task_gui_url: str | None


class GetListsResult(TypedDict):
    """
    Result structure for get_lists tool.

    Compatible with OffsetResponse protocol when offset fields are present.
    """

    success: bool
    folder_id: str | None
    lists: list[ToolList] | None
    count: int | None
    current_offset: int | None
    next_offset: int | None
    is_last: bool | None
    error: str | None
    message: str | None


class CreateTaskResult(TypedDict):
    """Result structure for create_task tool."""

    success: bool
    task: ToolTask | None
    message: str | None
    error: str | None


class UpdateTaskResult(TypedDict):
    """Result structure for update_task tool."""

    success: bool
    task: ToolTask | None
    message: str | None
    error: str | None


class ToolListStatus(TypedDict):
    """Simplified status information for a list."""

    status: str
    orderindex: int | None
    type: str | None
    color: str | None


class GetPossibleStatusesResult(TypedDict):
    """Result structure for get_possible_statuses_for_list tool."""

    success: bool
    list_id: str | None
    statuses: list[ToolListStatus] | None
    error: str | None
    message: str | None


class TaskAssignee(TypedDict):
    """Assignee information."""

    id: str
    name: str


class TaskAssigneeUpdateResult(TypedDict):
    """Result structure for update_task_assignees tool."""

    success: bool
    task_id: str
    task_name: str
    task_gui_url: NotRequired[str | None]
    assignees: list[TaskAssignee] | None
    operations_summary: str
    message: str
    error: str | None


class GetPossibleStatusesToolResult(TypedDict):
    """Result structure for get_possible_statuses_for_list tool."""

    success: bool
    list_id: str
    statuses: list[ToolListStatus]


class ToolComment(TypedDict):
    """Simplified comment information for tool outputs."""

    id: str
    text: str
    user_id: str
    user_name: str
    resolved: bool | None
    assignee_id: str | None
    assignee_name: str | None
    assigned_by_id: str | None
    assigned_by_name: str | None
    date: str | None
    reply_count: int | None


class GetTaskCommentsResult(TypedDict):
    """Result structure for get_task_comments tool."""

    success: bool
    task_id: str
    comments: list[ToolComment]
    total_comments: int
    oldest_comment_id: str | None
    message: str
    error: str | None


class CreateCommentResult(TypedDict):
    """Result structure for create_comment tool."""

    success: bool
    comment: ToolComment
    task_id: str
    message: str
    error: str | None


class UpdateCommentResult(TypedDict):
    """Result structure for update_comment tool."""

    success: bool
    comment: ToolComment
    task_id: str
    message: str
    error: str | None


class GetCommentRepliesResult(TypedDict):
    """
    Result structure for get_comment_replies tool.

    Compatible with OffsetResponse protocol when offset fields are present.
    """

    success: bool
    parent_comment_id: str
    replies: list[ToolComment]
    items_returned: NotRequired[int | None]
    current_offset: NotRequired[int | None]
    next_offset: NotRequired[int | None]
    is_last: NotRequired[bool | None]
    message: str
    error: str | None


class CreateCommentReplyResult(TypedDict):
    """Result structure for create_comment_reply tool."""

    success: bool
    reply: ToolComment
    parent_comment_id: str
    message: str
    error: str | None


class UserProfile(TypedDict):
    """User profile information for index tool (minimal data)."""

    id: int
    name: str
    email: str | None


class SpaceInfo(TypedDict):
    """Space information for index tool (minimal data)."""

    id: str
    name: str
    private: bool


class TaskSummaryInfo(TypedDict):
    """Task summary information for a formatted task (minimal data)."""

    id: str
    name: str
    status: str
    gui_url: str
    due_date: str | None
    last_updated: str | None
    list_name: str | None
    folder_name: str | None
    list_id: str | None
    folder_id: str | None


class TaskSummary(TypedDict):
    """Task summary statistics."""

    total_tasks_last_month: int
    open_tasks: int
    closed_tasks: int
    overdue_tasks: int
    tasks_with_due_dates: int
    top_due_tasks: list[TaskSummaryInfo]
    recently_updated_tasks: list[TaskSummaryInfo]
    data_disclaimer: str


class TaskSummaryError(TypedDict):
    """Task summary error state."""

    error: str


class MemberInfo(TypedDict):
    """Team member information."""

    id: int
    name: str
    email: str


class MemberStatistics(TypedDict):
    """Individual member task statistics."""

    member_info: MemberInfo
    total_tasks: int
    open_tasks: int
    closed_tasks: int
    overdue_tasks: int


class TeamTaskInfo(TypedDict):
    """Task information with assignee for team insights."""

    task: TaskSummaryInfo
    assignee: str


class TeamSummary(TypedDict):
    """Team-wide task statistics."""

    total_tasks_last_month: int
    open_tasks: int
    closed_tasks: int
    overdue_tasks: int


class TeamInsights(TypedDict):
    """Team management insights."""

    team_size: int
    team_summary: TeamSummary | None
    member_statistics: list[MemberStatistics] | None
    top_10_updated_tasks: list[TeamTaskInfo] | None
    top_10_overdue_tasks: list[TeamTaskInfo] | None
    data_disclaimer: str | None
    message: str | None
    error: str | None


class ContainerStats(TypedDict):
    """Statistics for a ClickUp container (space, folder, or list)."""

    id: str
    name: str
    task_count: int
    open_tasks: int
    closed_tasks: int
    last_month_tasks: int


class ContainerInsights(TypedDict):
    """Container distribution insights."""

    top_5_spaces: list[ContainerStats] | None
    top_5_folders: list[ContainerStats] | None
    top_5_lists: list[ContainerStats] | None
    data_disclaimer: str | None
    message: str | None
    error: str | None


class WorkspaceInfo(TypedDict):
    """Workspace information for index tool (minimal data)."""

    workspace_id: str
    name: str
    member_count: int
    spaces: list[SpaceInfo]
    task_summary: dict | None  # Can be TaskSummary, TaskSummaryError, or None
    team_insights: TeamInsights | None
    container_insights: ContainerInsights | None


class AgentGuidance(TypedDict):
    """Internal agent guidance (not for user display)."""

    internal_note: str
    clickup_hierarchy: str
    structure_explanation: str
    critical_reminders: list[str]
    workflow_patterns: list[str]
    tool_usage_tips: list[str]


class SystemGuidanceResult(TypedDict):
    """Static system guidance wrapper result."""

    agent_guidance: AgentGuidance


class ShortWorkspace(TypedDict):
    """Short workspace info with only essential identifiers."""

    id: str
    name: str


class WhoIAmResult(TypedDict):
    """Result for who_i_am tool with user profile and short workspace list."""

    who_i_am: UserProfile
    workspaces: list[ShortWorkspace]
    total_workspaces: int


class IndexResult(TypedDict):
    """Result structure for index tool."""

    who_i_am: UserProfile
    workspaces: list[WorkspaceInfo]
    total_workspaces: int
    agent_guidance: NotRequired[AgentGuidance | None]


# Fuzzy Search Tool Models
# These models are specifically for fuzzy search tool responses


class SimplifiedTask(TypedDict):
    """Simplified task model for fuzzy search results."""

    id: str
    name: str
    match_score: float


class SimplifiedList(TypedDict):
    """Simplified list model for fuzzy search results."""

    id: str
    name: str
    match_score: float
    archived: bool
    folder_id: str
    folder_name: str
    space_id: str
    space_name: str
    task_count: int


class SimplifiedFolder(TypedDict):
    """Simplified folder model for fuzzy search results."""

    id: str
    name: str
    match_score: float
    archived: bool
    space_id: str
    space_name: str
    task_count: int


class SimplifiedMember(TypedDict):
    """Simplified member model for fuzzy search results."""

    id: str
    name: str
    email: str
    match_score: float


class FuzzySearchTasksResponse(TypedDict):
    """Response from fuzzy search tasks."""

    query: str
    total_scanned: int
    total_matches: int
    tasks: list[SimplifiedTask]


class FuzzySearchListsResponse(TypedDict):
    """Response from fuzzy search lists."""

    query: str
    total_scanned: int
    total_matches: int
    lists: list[SimplifiedList]


class FuzzySearchFoldersResponse(TypedDict):
    """Response from fuzzy search folders."""

    query: str
    total_scanned: int
    total_matches: int
    folders: list[SimplifiedFolder]


class FuzzySearchMembersResponse(TypedDict):
    """Response from fuzzy search members."""

    query: str
    total_scanned: int
    total_matches: int
    members: list[SimplifiedMember]
