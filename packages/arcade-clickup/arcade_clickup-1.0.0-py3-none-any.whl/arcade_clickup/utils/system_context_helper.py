"""
System context helper functions.

This module provides utilities for system context, including task processing,
team insights generation, and data mapping used by overview/context tools.
"""

import asyncio
import time
from typing import Any

from arcade_clickup.models.tool_models import (
    AgentGuidance,
    ContainerInsights,
    ContainerStats,
    IndexResult,
    MemberInfo,
    MemberStatistics,
    ShortWorkspace,
    SpaceInfo,
    TaskSummary,
    TaskSummaryError,
    TaskSummaryInfo,
    TeamInsights,
    TeamSummary,
    TeamTaskInfo,
    UserProfile,
    WorkspaceInfo,
)


def map_user_to_profile(user_data: dict[str, Any]) -> UserProfile:
    """Map API user data to UserProfile model."""
    user = user_data.get("user", {})
    return UserProfile(
        id=user.get("id"),
        name=user.get("username", "Unknown User"),
        email=user.get("email"),
    )


def map_workspace_to_short_model(api_workspace: dict[str, Any]) -> ShortWorkspace:
    """Convert API workspace dict to a short model with only id and name."""
    return ShortWorkspace(
        id=str(api_workspace.get("id", "")),
        name=str(api_workspace.get("name", "")),
    )


def map_workspace_to_info(workspace: dict[str, Any]) -> WorkspaceInfo:
    """Map API workspace data to WorkspaceInfo model."""
    return WorkspaceInfo(
        workspace_id=workspace.get("id") or "",
        name=workspace.get("name") or "",
        member_count=len(workspace.get("members", [])),
        spaces=[],
        task_summary=None,
        team_insights=None,
        container_insights=None,
    )


def map_space_to_info(space: dict[str, Any]) -> SpaceInfo:
    """Map API space data to SpaceInfo model."""
    return SpaceInfo(
        id=space.get("id") or "",
        name=space.get("name") or "",
        private=space.get("private", False),
    )


def is_task_closed(task: dict[str, Any]) -> bool:
    """Check if a task is closed/completed based on its status."""
    status = task.get("status", {})
    if isinstance(status, dict):
        status_type = status.get("type", "").lower()
        status_status = status.get("status", "").lower()
        # Common closed status indicators
        return status_type == "closed" or status_status in [
            "complete",
            "completed",
            "done",
            "closed",
        ]
    return False


def format_task_for_summary(task: dict[str, Any]) -> TaskSummaryInfo:
    """Format task data for summary display."""
    import datetime

    task_summary = TaskSummaryInfo(
        id=task.get("id", ""),
        name=task.get("name", "Untitled Task"),
        status=task.get("status", {}).get("status", "Unknown"),
        gui_url=task.get("url", ""),
        due_date=task.get("due_date"),
        last_updated=task.get("date_updated"),
        list_name=task.get("list", {}).get("name"),
        folder_name=task.get("folder", {}).get("name"),
        list_id=task.get("list", {}).get("id"),
        folder_id=task.get("folder", {}).get("id"),
    )

    # Add due date if present
    if task.get("due_date"):
        try:
            due_timestamp = int(task["due_date"]) / 1000  # Convert from ms to seconds
            due_date = datetime.datetime.fromtimestamp(due_timestamp)
            task_summary["due_date"] = due_date.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            task_summary["due_date"] = "Invalid date"

    # Add last updated if present
    if task.get("date_updated"):
        try:
            updated_timestamp = int(task["date_updated"]) / 1000
            updated_date = datetime.datetime.fromtimestamp(updated_timestamp)
            task_summary["last_updated"] = updated_date.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            task_summary["last_updated"] = "Invalid date"

    # Add list/folder context if available
    if task.get("list", {}).get("name"):
        task_summary["list_name"] = task["list"]["name"]
    if task.get("list", {}).get("id"):
        task_summary["list_id"] = task["list"]["id"]

    if task.get("folder", {}).get("name"):
        task_summary["folder_name"] = task["folder"]["name"]
    if task.get("folder", {}).get("id"):
        task_summary["folder_id"] = task["folder"]["id"]

    return task_summary


def create_task_summary(all_tasks: list[dict[str, Any]]) -> TaskSummary:
    """Create task summary statistics from task list."""
    current_time = int(time.time() * 1000)

    # Calculate task statistics
    open_tasks = [t for t in all_tasks if not is_task_closed(t)]
    closed_tasks = [t for t in all_tasks if is_task_closed(t)]

    # Count overdue tasks (only open tasks)
    overdue_tasks = [
        t for t in open_tasks if t.get("due_date") and int(t.get("due_date", 0)) < current_time
    ]

    # Get top 5 tasks with due dates (open tasks only)
    tasks_with_due_dates = [t for t in open_tasks if t.get("due_date")]
    tasks_with_due_dates.sort(key=lambda x: int(x.get("due_date", 0)))
    top_due_tasks = tasks_with_due_dates[:5]

    # Get top 5 recently updated tasks (all tasks)
    top_updated_tasks = all_tasks[:5]  # Already ordered by updated

    return TaskSummary(
        total_tasks_last_month=len(all_tasks),
        open_tasks=len(open_tasks),
        closed_tasks=len(closed_tasks),
        overdue_tasks=len(overdue_tasks),
        tasks_with_due_dates=len(tasks_with_due_dates),
        top_due_tasks=[format_task_for_summary(t) for t in top_due_tasks],
        recently_updated_tasks=[format_task_for_summary(t) for t in top_updated_tasks],
        data_disclaimer=(
            "Stats based on up to 100 tasks from last 30 days. There may be more tasks not "
            "included in this summary."
        ),
    )


def create_task_summary_error() -> TaskSummaryError:
    """Create task summary error state."""
    return TaskSummaryError(error="Could not fetch task data")


def create_team_insights(
    team_members: list[dict[str, Any]],
    all_team_tasks: list[dict[str, Any]],
    current_user_id: int,
) -> TeamInsights:
    """Create team insights from team members and tasks."""
    current_time = int(time.time() * 1000)

    # Collect all team member IDs (excluding current user for team view)
    member_ids = []
    member_info_map = {}

    for member in team_members:
        user = member.get("user", {})
        user_id = user.get("id")
        if user_id and user_id != current_user_id:  # Exclude current user from team stats
            member_ids.append(user_id)
            member_info_map[user_id] = MemberInfo(
                id=user_id,
                name=user.get("username", "Unknown User"),
                email=user.get("email", ""),
            )

    if not member_ids:
        return TeamInsights(
            team_size=0,
            team_summary=None,
            member_statistics=None,
            top_10_updated_tasks=None,
            top_10_overdue_tasks=None,
            data_disclaimer=None,
            message="No other team members found in workspace",
            error=None,
        )

    # Organize tasks by team member
    member_stats = {}
    all_updated_tasks = []
    all_overdue_tasks = []

    for task in all_team_tasks:
        assignees = task.get("assignees", [])

        for assignee in assignees:
            assignee_id = assignee.get("id")
            if assignee_id in member_info_map:
                # Initialize member stats if not exists
                if assignee_id not in member_stats:
                    member_stats[assignee_id] = MemberStatistics(
                        member_info=member_info_map[assignee_id],
                        total_tasks=0,
                        open_tasks=0,
                        closed_tasks=0,
                        overdue_tasks=0,
                    )

                # Count task statistics
                member_stats[assignee_id]["total_tasks"] += 1

                is_closed = is_task_closed(task)
                if is_closed:
                    member_stats[assignee_id]["closed_tasks"] += 1
                else:
                    member_stats[assignee_id]["open_tasks"] += 1

                    # Check if overdue
                    if task.get("due_date") and int(task.get("due_date", 0)) < current_time:
                        member_stats[assignee_id]["overdue_tasks"] += 1
                        all_overdue_tasks.append(
                            TeamTaskInfo(
                                task=format_task_for_summary(task),
                                assignee=member_info_map[assignee_id]["name"],
                            )
                        )

                # Add to updated tasks list
                all_updated_tasks.append(
                    TeamTaskInfo(
                        task=format_task_for_summary(task),
                        assignee=member_info_map[assignee_id]["name"],
                    )
                )

    # Get top 10 recently updated and overdue tasks
    top_updated_tasks = all_updated_tasks[:10]

    # Sort overdue tasks by due date (earliest first) and take top 10
    overdue_with_dates = [item for item in all_overdue_tasks if item["task"].get("due_date")]
    overdue_with_dates.sort(key=lambda x: x["task"]["due_date"] or "0")
    top_overdue_tasks = overdue_with_dates[:10]

    # Calculate team totals
    total_team_tasks = sum(stats["total_tasks"] for stats in member_stats.values())
    total_open_tasks = sum(stats["open_tasks"] for stats in member_stats.values())
    total_closed_tasks = sum(stats["closed_tasks"] for stats in member_stats.values())
    total_overdue_tasks = sum(stats["overdue_tasks"] for stats in member_stats.values())

    # Get top 5 members by total tasks (open + closed)
    sorted_member_stats = sorted(
        member_stats.values(), key=lambda stats: stats["total_tasks"], reverse=True
    )
    top_5_member_stats = sorted_member_stats[:5]

    return TeamInsights(
        team_size=len(member_info_map),
        team_summary=TeamSummary(
            total_tasks_last_month=total_team_tasks,
            open_tasks=total_open_tasks,
            closed_tasks=total_closed_tasks,
            overdue_tasks=total_overdue_tasks,
        ),
        member_statistics=top_5_member_stats,
        top_10_updated_tasks=top_updated_tasks,
        top_10_overdue_tasks=top_overdue_tasks,
        data_disclaimer=(
            "Team stats based on up to 100 tasks from last 30 days. Excludes current user's "
            "tasks. Member statistics limited to top 5 by task count."
        ),
        message=None,
        error=None,
    )


def create_team_insights_error() -> TeamInsights:
    """Create team insights error state."""
    return TeamInsights(
        team_size=0,
        team_summary=None,
        member_statistics=None,
        top_10_updated_tasks=None,
        top_10_overdue_tasks=None,
        data_disclaimer=None,
        message=None,
        error="Could not fetch team insights",
    )


def _get_container_info(task: dict[str, Any], container_type: str) -> tuple[str, str]:
    """Get container ID and name from task."""
    container_info = task.get(container_type)
    if not container_info or not isinstance(container_info, dict):
        return "", ""
    return container_info.get("id", ""), container_info.get("name", "")


def create_container_stats(
    all_tasks: list[dict[str, Any]],
    container_type: str,
    all_containers: list[dict[str, Any]] | None = None,
) -> list[ContainerStats]:
    """Create container statistics from tasks.

    Args:
        all_tasks: List of tasks from API
        container_type: 'space', 'folder', or 'list'
        all_containers: Optional list of all available containers to fill up to 5 items

    Returns:
        List of container statistics sorted by task count (descending), limited to top 5
    """
    current_time = int(time.time() * 1000)
    month_ago = current_time - (30 * 24 * 60 * 60 * 1000)

    container_stats = {}

    # First, process all containers that have tasks
    for task in all_tasks:
        # Get container info based on type
        container_id, container_name = _get_container_info(task, container_type)
        if not container_id or not container_name:
            continue

        # Initialize container stats if not exists
        if container_id not in container_stats:
            container_stats[container_id] = ContainerStats(
                id=container_id,
                name=container_name,
                task_count=0,
                open_tasks=0,
                closed_tasks=0,
                last_month_tasks=0,
            )

        # Count task statistics
        container_stats[container_id]["task_count"] += 1

        is_closed = is_task_closed(task)
        if is_closed:
            container_stats[container_id]["closed_tasks"] += 1
        else:
            container_stats[container_id]["open_tasks"] += 1

        # Count tasks from last month
        task_updated = task.get("date_updated")
        if task_updated and int(task_updated) >= month_ago:
            container_stats[container_id]["last_month_tasks"] += 1

    # Sort by task count (descending)
    sorted_containers = sorted(
        container_stats.values(), key=lambda stats: stats["task_count"], reverse=True
    )

    # If we have fewer than 5 containers and all_containers is provided, fill up
    if len(sorted_containers) < 5 and all_containers:
        existing_ids = {stats["id"] for stats in sorted_containers}

        for container in all_containers:
            if len(sorted_containers) >= 5:
                break

            container_id = container.get("id", "")
            container_name = container.get("name", "")

            # Skip if already in our results or missing required fields
            if not container_id or not container_name or container_id in existing_ids:
                continue

            # Add container with 0 tasks
            sorted_containers.append(
                ContainerStats(
                    id=container_id,
                    name=container_name,
                    task_count=0,
                    open_tasks=0,
                    closed_tasks=0,
                    last_month_tasks=0,
                )
            )

    return sorted_containers[:5]


def create_container_insights(
    all_tasks: list[dict[str, Any]], all_spaces: list[dict[str, Any]] | None = None
) -> ContainerInsights:
    """Create container insights from tasks."""
    if not all_tasks:
        return ContainerInsights(
            top_5_spaces=None,
            top_5_folders=None,
            top_5_lists=None,
            data_disclaimer=None,
            message="No tasks available for container analysis",
            error=None,
        )

    # Generate statistics for each container type
    # For spaces, we can use all_spaces to fill up to 5 items
    top_spaces = create_container_stats(all_tasks, "space", all_spaces)

    # For folders and lists, we extract available containers from tasks
    # Since we don't have a direct API to get all folders/lists, we use what's available in tasks
    all_folders = []
    all_lists = []
    seen_folders = set()
    seen_lists = set()

    for task in all_tasks:
        # Extract unique folders
        folder_info = task.get("folder")
        if folder_info and isinstance(folder_info, dict):
            folder_id = folder_info.get("id")
            if folder_id and folder_id not in seen_folders:
                seen_folders.add(folder_id)
                all_folders.append(folder_info)

        # Extract unique lists
        list_info = task.get("list")
        if list_info and isinstance(list_info, dict):
            list_id = list_info.get("id")
            if list_id and list_id not in seen_lists:
                seen_lists.add(list_id)
                all_lists.append(list_info)

    top_folders = create_container_stats(all_tasks, "folder", all_folders)
    top_lists = create_container_stats(all_tasks, "list", all_lists)

    return ContainerInsights(
        top_5_spaces=top_spaces if top_spaces else None,
        top_5_folders=top_folders if top_folders else None,
        top_5_lists=top_lists if top_lists else None,
        data_disclaimer=(
            "Container stats based on up to 100 tasks (team-wide if permitted, otherwise user "
            "tasks). Last month data filters to 30 days. Empty containers added to reach 5 items "
            "when available."
        ),
        message=None,
        error=None,
    )


def create_container_insights_error() -> ContainerInsights:
    """Create container insights error state."""
    return ContainerInsights(
        top_5_spaces=None,
        top_5_folders=None,
        top_5_lists=None,
        data_disclaimer=None,
        message=None,
        error="Could not fetch container insights",
    )


def create_agent_guidance() -> AgentGuidance:
    """Create agent guidance object."""
    return AgentGuidance(
        internal_note=(
            "This section is for AI agent internal use only and should never be displayed to "
            "the end user"
        ),
        clickup_hierarchy=(
            "Workspace (also called a 'team') → Space → Folder (also called a 'project') → "
            "List (also called a 'task board') → Task"
        ),
        structure_explanation=(
            "Workspaces contain Spaces (departments/teams). Spaces contain Folders (projects). "
            "Folders contain Lists (task boards). Lists contain Tasks."
        ),
        critical_reminders=[
            (
                "Workspaces (also called teams in ClickUp) are the top-level organizational units "
                "that contain all of a team's data including spaces, folders, lists, and tasks."
            ),
            (
                "Each List has its own custom status set - always check available statuses before "
                "updating task status"
            ),
            "Tasks can only be created within Lists, not directly in Folders or Spaces",
            (
                "Always check the available statuses for a list before changing any task status "
                "within that list"
            ),
            (
                "When need for deep hierarchy navigation due not enough context about the item you "
                "are asked to look for, prioritize using the fuzzy search tools to try to find the "
                "item"
            ),
        ],
        workflow_patterns=[
            (
                "Not ideally for tasks operations, when fuzzy search did not find the item or you "
                "don't know what you are looking for, you need to: 1. Identify workspace → "
                "2. Find relevant space → 3. Locate project folder → 4. Access task list"
            ),
            "For task status updates: identify task → get list statuses → update with valid status",
        ],
        tool_usage_tips=[
            (
                "Fuzzy matching by name is not supported. Use the insights tool to retrieve a list "
                "of the latest updated items to help identify and suggest relevant items to "
                "the user."
            ),
            (
                "If the user is searching for a specific task and cannot find it by name, retrieve "
                "the latest updated tasks and suggest possible matches to the user."
            ),
        ],
    )


def create_index_result(
    who_i_am: UserProfile,
    workspaces: list[WorkspaceInfo],
    total_workspaces: int,
    include_agent_guidance: bool = False,
) -> IndexResult:
    """Create the final index result."""
    result: IndexResult = {
        "who_i_am": who_i_am,
        "workspaces": workspaces,
        "total_workspaces": total_workspaces,
    }
    if include_agent_guidance:
        result["agent_guidance"] = create_agent_guidance()

    return result


async def _fetch_workspace_spaces(api_client: Any, workspace_id: str) -> list[SpaceInfo]:
    """Fetch and map spaces for a workspace with graceful error handling."""
    try:
        spaces_response = await api_client.get_spaces(
            workspace_id=workspace_id, include_archived=False
        )
        spaces = spaces_response.get("spaces", [])[:3]  # Limit to 3 spaces
        return [map_space_to_info(space) for space in spaces]
    except Exception:
        return []


async def _fetch_user_task_summary(
    api_client: Any, workspace_id: str, user_id: int
) -> TaskSummary | TaskSummaryError:
    """Fetch and create task summary for a user with graceful error handling."""
    try:
        current_time = int(time.time() * 1000)  # ClickUp uses milliseconds
        month_ago = current_time - (30 * 24 * 60 * 60 * 1000)  # 30 days ago

        tasks_response = await api_client.get_filtered_team_tasks(
            workspace_id=workspace_id,
            request={
                "assignees": [user_id],
                "date_updated_gt": str(month_ago),
                "order_by": "updated",
                "reverse": "true",  # Most recently updated first
                "include_closed": "true",  # Include all statuses for stats
            },
            limit=100,  # Max from API
        )

        all_tasks = tasks_response.get("tasks", [])
        return create_task_summary(all_tasks)
    except Exception:
        return create_task_summary_error()


def _extract_team_member_ids(team_members: list[dict[str, Any]], current_user_id: int) -> list[int]:
    """Extract team member IDs excluding the current user."""
    member_ids = []
    for member in team_members:
        user = member.get("user", {})
        user_id = user.get("id")
        if user_id and user_id != current_user_id:
            member_ids.append(user_id)
    return member_ids


async def _fetch_team_tasks(
    api_client: Any, workspace_id: str, member_ids: list[int]
) -> list[dict[str, Any]]:
    """Fetch tasks for team members."""
    if not member_ids:
        return []

    current_time = int(time.time() * 1000)
    month_ago = current_time - (30 * 24 * 60 * 60 * 1000)

    team_tasks_response = await api_client.get_filtered_team_tasks(
        workspace_id=workspace_id,
        request={
            "assignees": member_ids,
            "date_updated_gt": str(month_ago),
            "order_by": "updated",
            "reverse": "true",
            "include_closed": "true",
        },
        limit=100,
    )
    return team_tasks_response.get("tasks", [])  # type: ignore[no-any-return]


async def _fetch_team_insights(
    api_client: Any, workspace_id: str, current_user_id: int
) -> TeamInsights:
    """Fetch and create team insights with graceful error handling."""
    try:
        # Get workspace details to get team members
        workspace_details = await api_client.get_workspace_details(workspace_id)
        team_members = workspace_details.get("members", [])

        # Get team member IDs (excluding current user)
        member_ids = _extract_team_member_ids(team_members, current_user_id)

        # Get tasks for team members
        all_team_tasks = await _fetch_team_tasks(api_client, workspace_id, member_ids)

        return create_team_insights(team_members, all_team_tasks, current_user_id)
    except Exception:
        return create_team_insights_error()


async def _fetch_workspace_data(
    api_client: Any,
    workspace_id: str,
    user_id: int,
    include_task_summary: bool,
    include_team_insights: bool,
    include_container_insights: bool,
) -> tuple[list[SpaceInfo], list[dict[str, Any]], list[dict[str, Any]] | None]:
    """Fetch all required workspace data with minimal API calls.

    Returns:
        tuple: (spaces, all_tasks, team_members_if_needed)
    """
    # Determine what data we need
    need_tasks = include_task_summary or include_container_insights
    need_team_data = include_team_insights

    # Parallel fetch of basic data
    spaces_task = asyncio.create_task(_fetch_workspace_spaces(api_client, workspace_id))

    tasks_data = []
    team_members = None

    if need_tasks or need_team_data:
        try:
            # Try to get comprehensive task data (team-wide if possible)
            all_tasks_response = await api_client.get_filtered_team_tasks(
                workspace_id=workspace_id,
                request={
                    "order_by": "updated",
                    "reverse": "true",
                    "include_closed": "true",
                    # No date filter to get maximum data for all features
                },
                limit=100,
            )
            tasks_data = all_tasks_response.get("tasks", [])

            # If we got no team tasks, fall back to user tasks
            if not tasks_data and need_tasks:
                user_tasks_response = await api_client.get_filtered_team_tasks(
                    workspace_id=workspace_id,
                    request={
                        "assignees": [user_id],
                        "order_by": "updated",
                        "reverse": "true",
                        "include_closed": "true",
                    },
                    limit=100,
                )
                tasks_data = user_tasks_response.get("tasks", [])

        except Exception:
            tasks_data = []

    # Fetch team members only if needed for team insights
    if need_team_data:
        try:
            workspace_details = await api_client.get_workspace_details(workspace_id)
            team_members = workspace_details.get("members", [])
        except Exception:
            team_members = []

    # Wait for spaces to complete
    spaces = await spaces_task

    return spaces, tasks_data, team_members


async def process_workspace_data(
    api_client: Any,
    workspace: dict[str, Any],
    who_i_am: UserProfile,
    include_task_summary: bool,
    include_team_insights: bool,
    include_container_insights: bool,
) -> WorkspaceInfo:
    """Process a single workspace and gather all its data."""
    workspace_id = workspace.get("id")
    workspace_info = map_workspace_to_info(workspace)
    user_id = who_i_am["id"]

    _initialize_optional_fields(
        workspace_info, include_task_summary, include_team_insights, include_container_insights
    )

    # Fetch all required data with minimal API calls
    spaces, all_tasks, team_members = await _fetch_workspace_data(
        api_client,
        workspace_id or "",
        user_id,
        include_task_summary,
        include_team_insights,
        include_container_insights,
    )

    workspace_info["spaces"] = spaces

    if include_task_summary:
        workspace_info["task_summary"] = _process_task_summary(all_tasks, user_id)  # type: ignore[typeddict-item]

    if include_team_insights:
        workspace_info["team_insights"] = _process_team_insights(team_members, all_tasks, user_id)

    if include_container_insights:
        workspace_info["container_insights"] = _process_container_insights(all_tasks, spaces)

    return workspace_info


def _initialize_optional_fields(
    workspace_info: WorkspaceInfo,
    include_task_summary: bool,
    include_team_insights: bool,
    include_container_insights: bool,
) -> None:
    """Initialize optional fields based on inclusion flags."""
    if not include_task_summary:
        workspace_info["task_summary"] = None
    if not include_team_insights:
        workspace_info["team_insights"] = None
    if not include_container_insights:
        workspace_info["container_insights"] = None


def _process_task_summary(
    all_tasks: list[dict[str, Any]], user_id: int
) -> TaskSummary | TaskSummaryError:
    """Process task summary for a user."""
    try:
        if all_tasks:
            # Filter tasks for user and apply date filtering for task summary
            current_time = int(time.time() * 1000)
            month_ago = current_time - (30 * 24 * 60 * 60 * 1000)

            user_tasks = [
                task
                for task in all_tasks
                if any(assignee.get("id") == user_id for assignee in task.get("assignees", []))
                and task.get("date_updated")
                and int(task.get("date_updated", 0)) >= month_ago
            ]
            return create_task_summary(user_tasks)
        else:
            # No tasks means API likely failed
            return create_task_summary_error()
    except Exception:
        return create_task_summary_error()


def _process_team_insights(
    team_members: list[dict[str, Any]] | None,
    all_tasks: list[dict[str, Any]],
    user_id: int,
) -> TeamInsights:
    """Process team insights."""
    try:
        if team_members:
            # Filter tasks for team members (excluding current user)
            member_ids = _extract_team_member_ids(team_members, user_id)
            team_tasks = [
                task
                for task in all_tasks
                if any(assignee.get("id") in member_ids for assignee in task.get("assignees", []))
            ]
            return create_team_insights(team_members, team_tasks, user_id)
        else:
            return create_team_insights_error()
    except Exception:
        return create_team_insights_error()


def _process_container_insights(
    all_tasks: list[dict[str, Any]], spaces: list[SpaceInfo]
) -> ContainerInsights:
    """Process container insights."""
    try:
        # Convert SpaceInfo objects to dict format for container creation
        spaces_data = [{"id": space["id"], "name": space["name"]} for space in spaces]
        return create_container_insights(all_tasks, spaces_data)
    except Exception:
        return create_container_insights_error()
