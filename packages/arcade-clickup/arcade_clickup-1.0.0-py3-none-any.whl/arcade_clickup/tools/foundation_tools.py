"""
Foundation tools for ClickUp workspace and team member management.

These tools are used to get the workspaces, spaces, folders, lists, and team members from ClickUp.
"""

from typing import Annotated, Any

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import ClickUp

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.utils.helpers import (
    clean_dict,
    create_possible_statuses_result,
    execute_get_lists_for_space_workflow,
    map_folder_to_tool_model,
    map_list_statuses_to_tool_model,
    map_list_to_tool_model,
    map_member_to_tool_model,
    map_space_to_tool_model,
    raise_workspace_not_found_error,
    validate_workspace_id_and_raise,
)
from arcade_clickup.utils.offset_helper import OffsetHelper, OffsetParams


@tool(requires_auth=ClickUp())
async def get_spaces(
    context: ToolContext,
    workspace_id: Annotated[
        str, "The ClickUp workspace ID to get spaces from (should be a number)"
    ],
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of spaces to return (max: 50, default: 50)"] = 50,
    include_archived: Annotated[
        bool, "Whether to include archived spaces (default: False)"
    ] = False,
) -> Annotated[dict[str, Any], "List of spaces in the workspace"]:
    """
    Retrieve spaces from a ClickUp workspace.

    Use this tool when users ask for:
    - Spaces within a workspace (not folders or lists)
    - Available spaces to choose from before getting folders
    - Space discovery when you need to identify space IDs or names
    - High-level workspace organization structure

    Note: This is for spaces (top-level containers), not folders (which contain lists) nor lists.
    This tool fetches spaces from the specified workspace with support for offset-based retrieval
    and archived space filtering. Results are sorted alphabetically by name.
    """
    validate_workspace_id_and_raise(workspace_id)

    offset_params = OffsetParams(offset=offset, limit=limit, max_limit=50)

    api_client = ClickupApiClient(context)
    api_response = await api_client.get_spaces(
        workspace_id=workspace_id, include_archived=include_archived
    )

    raw_spaces = api_response.get("spaces", [])
    all_spaces = [map_space_to_tool_model(space, workspace_id) for space in raw_spaces]

    offset_result = OffsetHelper.offset_and_sort(
        items=all_spaces,
        offset_params=offset_params,
        sort_field="name",
    )

    # Create response using the offset helper
    response = OffsetHelper.create_offset_response(
        result=offset_result,
        success=True,
        workspace_id=workspace_id,
        spaces=offset_result.items,
    )

    return clean_dict(response)


@tool(requires_auth=ClickUp())
async def get_folders_for_space(
    context: ToolContext,
    space_id: Annotated[str, "The ClickUp space ID to get folders from"],
    workspace_id: Annotated[
        str, "The ClickUp workspace ID for GUI URL generation (should be a number)"
    ],
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of folders to return (max: 50, default: 50)"] = 50,
    include_archived: Annotated[
        bool,
        "Whether to include archived, inactive, or deleted folders (default: False)",
    ] = False,
) -> Annotated[dict[str, Any], "List of folders in the space"]:
    """
    Retrieve folders (also called directories, project categories, or project areas) from a
    ClickUp space.

    Only use this tool when you already have the space ID and want to see the folders within
    that specific space.

    Important: When users mention a space(or area),
    always use this tool to get the folders within that space.

    This tool fetches folders from the specified space with support for offset-based retrieval
    and archived folder filtering. Results are sorted alphabetically by name.
    """

    offset_params = OffsetParams(offset=offset, limit=limit, max_limit=50)

    api_client = ClickupApiClient(context)

    api_response = await api_client.get_folders(
        space_id=space_id, include_archived=include_archived
    )

    raw_folders = api_response.get("folders", [])
    all_folders = [map_folder_to_tool_model(folder, workspace_id) for folder in raw_folders]

    offset_result = OffsetHelper.offset_and_sort(
        items=all_folders,
        offset_params=offset_params,
        sort_field="name",
    )

    response = OffsetHelper.create_offset_response(
        result=offset_result,
        success=True,
        space_id=space_id,
        folders=offset_result.items,
    )

    return clean_dict(response)


@tool(requires_auth=ClickUp())
async def get_lists_for_folder(
    context: ToolContext,
    folder_id: Annotated[str, "The ClickUp folder ID (also called directory ID) to get lists from"],
    workspace_id: Annotated[
        str, "The ClickUp workspace ID for GUI URL generation (should be a number)"
    ],
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of lists to return (max: 50, default: 50)"] = 50,
    include_archived: Annotated[
        bool,
        "Whether to include archived, inactive, or completed lists (default: False)",
    ] = False,
) -> Annotated[dict[str, Any], "List of task lists in the folder"]:
    """
    Retrieve task lists from a ClickUp folder (when users refer to a folder as a "directory",
    they mean the same thing).

    Only use this tool when you already have the folder ID and want to see the lists within
    that specific folder.

    Important: When users mention a specific folder(or directory), always use this tool to get
    the lists within that folder.

    This tool fetches lists from the specified folder with support for offset-based retrieval
    and archived list filtering. Results are sorted alphabetically by name.
    """

    offset_params = OffsetParams(offset=offset, limit=limit, max_limit=50)

    api_client = ClickupApiClient(context)
    api_response = await api_client.get_lists(
        folder_id=folder_id, include_archived=include_archived
    )

    raw_lists = api_response.get("lists", [])
    all_lists = [map_list_to_tool_model(list_item, workspace_id) for list_item in raw_lists]

    offset_result = OffsetHelper.offset_and_sort(
        items=all_lists,
        offset_params=offset_params,
        sort_field="name",
    )

    response = OffsetHelper.create_offset_response(
        result=offset_result,
        success=True,
        folder_id=folder_id,
        lists=offset_result.items,
    )

    return clean_dict(response)


@tool(requires_auth=ClickUp())
async def get_lists_for_space(
    context: ToolContext,
    space_id: Annotated[str, "The ClickUp space ID to get lists from"],
    workspace_id: Annotated[
        str, "The ClickUp workspace ID for GUI URL generation (should be a number)"
    ],
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of lists to return (max: 50, default: 50)"] = 50,
    include_archived: Annotated[
        bool,
        "Whether to include archived, inactive, or completed lists (default: False)",
    ] = False,
) -> Annotated[dict[str, Any], "List of task lists from all folders in the space"]:
    """
    Retrieve all task lists from a ClickUp space by collecting lists from all folders within the
    space.

    Only use this tool when you have a space ID and want to see all lists across all folders
    within that space.

    This tool provides a comprehensive view of all lists in a space with support for offset-based
    retrieval and archived list filtering. Results are sorted alphabetically by name.
    """
    offset_params = OffsetParams(offset=offset, limit=limit, max_limit=50)

    api_client = ClickupApiClient(context)

    all_lists = await execute_get_lists_for_space_workflow(
        api_client=api_client,
        space_id=space_id,
        workspace_id=workspace_id,
        include_archived=include_archived,
    )

    offset_result = OffsetHelper.offset_and_sort(
        items=all_lists,
        offset_params=offset_params,
        sort_field="name",
    )

    response = OffsetHelper.create_offset_response(
        result=offset_result,
        success=True,
        space_id=space_id,
        lists=offset_result.items,
    )

    return clean_dict(response)


@tool(requires_auth=ClickUp())
async def get_statuses_for_list(
    context: ToolContext,
    list_id: Annotated[str, "The ClickUp list ID to retrieve possible task statuses for"],
) -> Annotated[
    dict[str, Any],
    "Possible statuses for a given list (useful when creating or updating tasks)",
]:
    """
    Retrieve the possible task statuses for a specific ClickUp list.

    Only use this tool when you already have the list ID and need to discover the valid
    statuses for that specific list.

    Use this tool to discover valid status labels and their ordering/type for a list
    before creating or updating tasks, since statuses can be customized per list.
    """
    api_client = ClickupApiClient(context)
    data = await api_client.get_list_details(list_id)

    raw_statuses = (data.get("statuses") or []) if isinstance(data, dict) else []
    statuses = map_list_statuses_to_tool_model(raw_statuses)

    result = create_possible_statuses_result(list_id, statuses)
    return clean_dict(dict(result))


@tool(requires_auth=ClickUp())
async def get_members_for_workspace(
    context: ToolContext,
    workspace_id: Annotated[
        str, "The ID of the ClickUp workspace to get team members from (should be a number)"
    ],
    offset: Annotated[int, "Starting position for offset-based retrieval (default: 0)"] = 0,
    limit: Annotated[int, "Maximum number of members to return (max: 50, default: 50)"] = 50,
) -> Annotated[dict[str, Any], "List of team members in the specified workspace"]:
    """
    Retrieve all team members from a specific ClickUp workspace.

    Only use this tool when you already have the workspace ID and need to see the members
    within that specific workspace.

    This tool fetches detailed information about all members of a ClickUp workspace,
    including their basic profile information and role within the workspace.
    Results are sorted and support offset-based retrieval.
    """
    validate_workspace_id_and_raise(workspace_id)

    offset_params = OffsetParams(offset=offset, limit=limit, max_limit=50)

    api_client = ClickupApiClient(context)
    workspace_details = await api_client.get_workspace_details(workspace_id)
    if not workspace_details:
        raise_workspace_not_found_error(workspace_id)

    workspace_name = workspace_details.get("name", f"Workspace {workspace_id}")

    members_data = workspace_details.get("members", [])
    all_members = [map_member_to_tool_model(member_data) for member_data in members_data]  # type: ignore[arg-type]

    offset_result = OffsetHelper.offset_and_sort(
        items=all_members,
        offset_params=offset_params,
        sort_field="name",
    )

    response = OffsetHelper.create_offset_response(
        result=offset_result,
        success=True,
        workspace_id=workspace_id,
        workspace_name=workspace_name,
        members=offset_result.items,
    )

    return clean_dict(response)
