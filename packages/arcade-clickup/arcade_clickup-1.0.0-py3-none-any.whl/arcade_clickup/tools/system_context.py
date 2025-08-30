"""
ClickUp system context and insights tools.

Tools included (all return TypedDict models converted via dict(...)):
- who_am_i: current user profile and accessible workspaces (teams) - FIRST tool to call
- get_system_guidance: static guidance for agents to make informed decisions (not for end users)
- get_workspace_insights: brief workspace overview using latest updated tasks to provide insights
"""

from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import ClickUp

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.models.tool_models import SystemGuidanceResult, WorkspaceInfo
from arcade_clickup.utils.helpers import (
    clean_dict,
    map_workspace_to_short_model,
    raise_workspace_not_found_error,
    validate_workspace_id_and_raise,
)
from arcade_clickup.utils.system_context_helper import (
    create_agent_guidance,
    map_user_to_profile,
    process_workspace_data,
)


@tool(requires_auth=ClickUp())
async def who_am_i(
    context: ToolContext,
) -> Annotated[
    dict,
    "The current user's profile information and accessible workspaces (teams). "
    + "This should be the first tool called.",
]:
    """
    Return current user profile and accessible workspaces (teams).

    This should be the FIRST tool called when starting any ClickUp interaction.

    Each workspace represents
    a separate team or organization with its own members, projects, and settings.
    """
    api_client = ClickupApiClient(context)
    user_data = await api_client.get_user()
    who_i_am_profile = map_user_to_profile(user_data)

    workspaces_response = await api_client.get_authorized_workspaces()
    teams = workspaces_response.get("teams", [])
    short_workspaces = [map_workspace_to_short_model(w) for w in teams]

    display_profile = {
        "my_clickup_id": who_i_am_profile.get("id"),
        "my_clickup_name": who_i_am_profile.get("name"),
        "my_email": who_i_am_profile.get("email"),
    }

    result = {
        "who_i_am": display_profile,
        "my_workspaces": short_workspaces,
        "total_workspaces": len(teams),
    }
    return clean_dict(dict(result))


@tool()
async def get_system_guidance(
    context: ToolContext,
) -> Annotated[
    dict,
    "Static guidance about ClickUp structure and usage tips",
]:
    """
    Return static guidance intended solely to help agents make informed decisions.

    Important: The guidance content is for internal agent use only and should not be
    displayed to end users.
    """
    guidance = create_agent_guidance()
    result: SystemGuidanceResult = {"agent_guidance": guidance}
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def get_workspace_insights(
    context: ToolContext,
    workspace_id: Annotated[str, "The ClickUp workspace ID to summarize (should be a number)"],
) -> Annotated[
    dict[str, Any],
    "Brief workspace overview leveraging latest updated tasks to deliver actionable insights",
]:
    """
    Return a brief overview for a workspace using the latest updated tasks to inform the user.

    Includes task summary, team insights, and container(space, folder, list) insights.
    """
    validate_workspace_id_and_raise(workspace_id)

    api_client = ClickupApiClient(context)
    ws_details = await api_client.get_workspace_details(workspace_id)

    if not ws_details:
        raise_workspace_not_found_error(workspace_id)

    workspace: dict[str, Any] = {
        "id": workspace_id,
        "name": ws_details.get("name", f"Workspace {workspace_id}")
        if isinstance(ws_details, dict)
        else f"Workspace {workspace_id}",
        "members": ws_details.get("members", []) if isinstance(ws_details, dict) else [],
    }

    who_i_am_profile = map_user_to_profile(await api_client.get_user())
    overview: WorkspaceInfo = await process_workspace_data(
        api_client=api_client,
        workspace=workspace,
        who_i_am=who_i_am_profile,
        include_task_summary=True,
        include_team_insights=True,
        include_container_insights=True,
    )

    return clean_dict(dict(overview))
