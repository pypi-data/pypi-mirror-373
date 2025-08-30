"""Fuzzy search helper functions following project patterns."""

import asyncio
from typing import Any

from arcade_clickup.client.api_client import ClickupApiClient
from arcade_clickup.constants import (
    FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    FUZZY_SEARCH_MAX_PAGES,
)
from arcade_clickup.models.tool_models import (
    FuzzySearchFoldersResponse,
    FuzzySearchListsResponse,
    FuzzySearchMembersResponse,
    FuzzySearchTasksResponse,
    SimplifiedFolder,
    SimplifiedList,
    SimplifiedMember,
    SimplifiedTask,
)
from arcade_clickup.utils import fuzzy_search_utils


async def execute_fuzzy_search_tasks_workflow(
    client: ClickupApiClient,
    workspace_id: str,
    query: str,
    scan_size: int = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    filters: dict[str, Any] | None = None,
    limit: int = 10,
) -> FuzzySearchTasksResponse:
    """Execute the complete fuzzy search tasks workflow."""
    scan_size = max(100, min(scan_size, FUZZY_SEARCH_MAX_PAGES * 100))
    scan_size = (scan_size // 100) * 100
    max_pages = scan_size // 100

    collected_tasks: list[dict[str, Any]] = []
    page = 0

    while page < max_pages:
        response = await client.get_team_tasks_for_fuzzy_search(
            workspace_id=workspace_id,
            page=page,
            filters=filters,
        )

        tasks = response.get("tasks", [])
        if not tasks:
            break

        collected_tasks.extend(tasks)
        page += 1

    matches_with_scores = fuzzy_search_utils.filter_and_rank_matches(
        collected_tasks,
        query,
        name_field="name",
    )

    # Limit results to limit
    limited_matches = matches_with_scores[:limit]

    simplified_tasks = [
        SimplifiedTask(
            id=task["id"],
            name=task["name"],
            match_score=score,
        )
        for task, score in limited_matches
    ]

    return FuzzySearchTasksResponse(
        query=query,
        total_scanned=len(collected_tasks),
        total_matches=len(simplified_tasks),
        tasks=simplified_tasks,
    )


async def execute_fuzzy_search_lists_workflow(
    client: ClickupApiClient,
    workspace_id: str,
    query: str,
    scan_size: int = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    space_ids: list[str] | None = None,
    folder_ids: list[str] | None = None,
    archived: bool = False,
    limit: int = 10,
) -> FuzzySearchListsResponse:
    """Execute fuzzy search workflow for lists."""
    collected_lists = await _get_lists_for_search(
        client, workspace_id, folder_ids, space_ids, scan_size, archived
    )

    matches_with_scores = fuzzy_search_utils.filter_and_rank_matches(
        collected_lists,
        query,
        name_field="name",
    )

    # Limit results to limit
    limited_matches = matches_with_scores[:limit]

    simplified_lists = [
        SimplifiedList(
            id=lst["id"],
            name=lst["name"],
            archived=lst.get("archived", False),
            task_count=lst.get("task_count", 0),
            space_id=lst.get("space_id", ""),
            space_name=lst.get("space_name", ""),
            folder_id=lst.get("folder_id", ""),
            folder_name=lst.get("folder_name", ""),
            match_score=score,
        )
        for lst, score in limited_matches
    ]

    return FuzzySearchListsResponse(
        query=query,
        total_scanned=len(collected_lists),
        total_matches=len(simplified_lists),
        lists=simplified_lists,
    )


async def execute_fuzzy_search_folders_workflow(
    client: ClickupApiClient,
    workspace_id: str,
    query: str,
    scan_size: int = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    space_ids: list[str] | None = None,
    archived: bool = False,
    limit: int = 10,
) -> FuzzySearchFoldersResponse:
    """Execute fuzzy search workflow for folders."""
    collected_folders: list[dict[str, Any]] = []
    spaces_to_search = space_ids if space_ids else []

    if not spaces_to_search:
        response = await client.get_spaces(workspace_id, include_archived=archived)
        spaces = response.get("spaces", [])
        spaces_to_search = [s["id"] for s in spaces]

    response = await client.get_spaces(workspace_id, include_archived=archived)
    spaces = response.get("spaces", [])
    space_names = {s["id"]: s["name"] for s in spaces}

    async def get_folders_for_space(space_id: str) -> list[dict[str, Any]]:
        folders_response = await client.get_folders(space_id, include_archived=archived)
        folders: list[dict[str, Any]] = folders_response.get("folders", [])
        for folder in folders:
            folder["space_id"] = space_id
            folder["space_name"] = space_names.get(space_id, "")
        return folders

    tasks = [get_folders_for_space(space_id) for space_id in spaces_to_search]
    folder_results = await asyncio.gather(*tasks)

    for folders in folder_results:
        collected_folders.extend(folders)
        if len(collected_folders) >= scan_size:
            collected_folders = collected_folders[:scan_size]
            break

    matches_with_scores = fuzzy_search_utils.filter_and_rank_matches(
        collected_folders,
        query,
        name_field="name",
    )

    # Limit results to limit
    limited_matches = matches_with_scores[:limit]

    simplified_folders = [
        SimplifiedFolder(
            id=folder["id"],
            name=folder["name"],
            archived=folder.get("archived", False),
            task_count=folder.get("task_count", 0),
            space_id=folder.get("space_id", ""),
            space_name=folder.get("space_name", ""),
            match_score=score,
        )
        for folder, score in limited_matches
    ]

    return FuzzySearchFoldersResponse(
        query=query,
        total_scanned=len(collected_folders),
        total_matches=len(simplified_folders),
        folders=simplified_folders,
    )


async def execute_fuzzy_search_members_workflow(
    client: ClickupApiClient,
    workspace_id: str,
    query: str,
    scan_size: int = FUZZY_SEARCH_DEFAULT_SCAN_SIZE,
    limit: int = 10,
) -> FuzzySearchMembersResponse:
    """Execute fuzzy search workflow for workspace members."""
    response = await client.get_workspace_details(workspace_id=workspace_id)

    members = response.get("members", [])

    # Prepare users with a searchable name field
    users_with_names: list[dict[str, Any]] = []
    for member in members:
        user_data = member.get("user", {})
        if isinstance(user_data, dict):
            # Create a copy with a searchable_name field
            user_copy = dict(user_data)
            # Use username if available, otherwise use email prefix
            username = user_data.get("username", "")
            if username:
                user_copy["searchable_name"] = username
            else:
                # Fallback to email prefix if no username
                email = user_data.get("email", "")
                if email and "@" in email:
                    user_copy["searchable_name"] = email.split("@")[0]
                else:
                    user_copy["searchable_name"] = email or str(user_data.get("id", ""))
            users_with_names.append(user_copy)

    matches_with_scores = fuzzy_search_utils.filter_and_rank_matches(
        users_with_names,
        query,
        name_field="searchable_name",
    )

    # Limit results to limit
    limited_matches = matches_with_scores[:limit]

    simplified_members = []
    for user, score in limited_matches:
        # Use searchable_name for display (which is username or email prefix)
        simplified_members.append(
            SimplifiedMember(
                id=str(user.get("id", "")),
                name=user.get("searchable_name", ""),
                email=user.get("email", ""),
                match_score=score,
            )
        )

    return FuzzySearchMembersResponse(
        query=query,
        total_scanned=len(users_with_names),
        total_matches=len(simplified_members),
        members=simplified_members,
    )


async def _build_folder_info_mapping(
    client: ClickupApiClient,
    spaces: list[dict[str, Any]],
    folder_ids: list[str],
    space_names: dict[str, str],
    archived: bool,
) -> dict[str, dict[str, str]]:
    """Build a mapping of folder_id to folder info."""

    async def get_folders_info_for_space(space: dict[str, Any]) -> dict[str, dict[str, str]]:
        space_id = space["id"]
        local_folder_info = {}
        folders_response = await client.get_folders(space_id, include_archived=archived)
        folders: list[dict[str, Any]] = folders_response.get("folders", [])
        for folder in folders:
            if folder["id"] in folder_ids:
                local_folder_info[folder["id"]] = {
                    "name": folder.get("name", ""),
                    "space_id": space_id,
                    "space_name": space_names.get(space_id, ""),
                }
        return local_folder_info

    tasks = [get_folders_info_for_space(space) for space in spaces]
    results = await asyncio.gather(*tasks)

    folder_info = {}
    for result in results:
        folder_info.update(result)

    return folder_info


async def _collect_lists_from_folders(
    client: ClickupApiClient,
    folder_ids: list[str],
    folder_info: dict[str, dict[str, str]],
    scan_size: int,
    archived: bool,
) -> list[dict[str, Any]]:
    """Collect lists from specified folders."""

    async def get_lists_for_folder(folder_id: str) -> list[dict[str, Any]]:
        response = await client.get_lists(folder_id, include_archived=archived)
        lists: list[dict[str, Any]] = response.get("lists", [])

        folder_data = folder_info.get(folder_id, {})
        for lst in lists:
            lst["folder_id"] = folder_id
            lst["folder_name"] = folder_data.get("name", "")
            lst["space_id"] = folder_data.get("space_id", "")
            lst["space_name"] = folder_data.get("space_name", "")

        return lists

    tasks = [get_lists_for_folder(folder_id) for folder_id in folder_ids]
    list_results = await asyncio.gather(*tasks)

    collected_lists: list[dict[str, Any]] = []
    for lists in list_results:
        collected_lists.extend(lists)
        if len(collected_lists) >= scan_size:
            collected_lists = collected_lists[:scan_size]
            break

    return collected_lists


async def _collect_lists_from_spaces(
    client: ClickupApiClient,
    workspace_id: str,
    space_ids: list[str] | None,
    scan_size: int,
    archived: bool,
) -> list[dict[str, Any]]:
    """Collect lists from spaces."""
    spaces_to_search = space_ids if space_ids else []

    if not spaces_to_search:
        response = await client.get_spaces(workspace_id, include_archived=archived)
        spaces = response.get("spaces", [])
        spaces_to_search = [s["id"] for s in spaces]

    response = await client.get_spaces(workspace_id, include_archived=archived)
    spaces = response.get("spaces", [])
    space_names = {s["id"]: s["name"] for s in spaces}

    async def get_lists_for_space_wrapper(space_id: str) -> list[dict[str, Any]]:
        space_lists: list[dict[str, Any]] = []
        await _collect_lists_from_single_space(client, space_id, space_names, space_lists, archived)
        return space_lists

    tasks = [get_lists_for_space_wrapper(space_id) for space_id in spaces_to_search]
    space_results = await asyncio.gather(*tasks)

    collected_lists: list[dict[str, Any]] = []
    for lists in space_results:
        collected_lists.extend(lists)
        if len(collected_lists) >= scan_size:
            collected_lists = collected_lists[:scan_size]
            break

    return collected_lists


async def _get_direct_space_lists(
    client: ClickupApiClient, space_id: str, space_names: dict[str, str], archived: bool
) -> list[dict[str, Any]]:
    """Get lists directly from a space."""
    response = await client.get_lists_from_space(space_id, archived=archived)
    space_lists: list[dict[str, Any]] = response.get("lists", [])
    for lst in space_lists:
        lst["space_id"] = space_id
        lst["space_name"] = space_names.get(space_id, "")
        lst["folder_id"] = ""
        lst["folder_name"] = ""
    return space_lists


async def _get_lists_for_folder(
    client: ClickupApiClient,
    folder: dict[str, Any],
    space_id: str,
    space_names: dict[str, str],
    archived: bool,
) -> list[dict[str, Any]]:
    """Get lists for a single folder."""
    folder_id = folder.get("id")
    if not folder_id:
        return []
    lists_response = await client.get_lists(folder_id, include_archived=archived)
    folder_lists: list[dict[str, Any]] = lists_response.get("lists", [])
    for lst in folder_lists:
        lst["space_id"] = space_id
        lst["space_name"] = space_names.get(space_id, "")
        lst["folder_id"] = folder_id
        lst["folder_name"] = folder.get("name", "")
    return folder_lists


async def _get_lists_from_folders(
    client: ClickupApiClient, space_id: str, space_names: dict[str, str], archived: bool
) -> list[dict[str, Any]]:
    """Get lists from all folders in a space."""
    folders_response = await client.get_folders(space_id, include_archived=archived)
    folders: list[dict[str, Any]] = folders_response.get("folders", [])

    folder_tasks = [
        _get_lists_for_folder(client, folder, space_id, space_names, archived) for folder in folders
    ]
    folder_results = await asyncio.gather(*folder_tasks)

    all_folder_lists = []
    for lists in folder_results:
        all_folder_lists.extend(lists)
    return all_folder_lists


async def _collect_lists_from_single_space(
    client: ClickupApiClient,
    space_id: str,
    space_names: dict[str, str],
    collected_lists: list[dict[str, Any]],
    archived: bool,
) -> None:
    """Collect lists from a single space."""
    direct_lists, folder_lists = await asyncio.gather(
        _get_direct_space_lists(client, space_id, space_names, archived),
        _get_lists_from_folders(client, space_id, space_names, archived),
    )

    collected_lists.extend(direct_lists)
    collected_lists.extend(folder_lists)


async def _get_lists_for_search(
    client: ClickupApiClient,
    workspace_id: str,
    folder_ids: list[str] | None,
    space_ids: list[str] | None,
    scan_size: int,
    archived: bool,
) -> list[dict[str, Any]]:
    """Get lists for fuzzy search based on folder or space filters."""
    if folder_ids:
        response = await client.get_spaces(workspace_id, include_archived=archived)
        spaces = response.get("spaces", [])
        space_names = {s["id"]: s["name"] for s in spaces}

        folder_info = await _build_folder_info_mapping(
            client, spaces, folder_ids, space_names, archived
        )

        return await _collect_lists_from_folders(
            client, folder_ids, folder_info, scan_size, archived
        )

    elif space_ids or not folder_ids:
        return await _collect_lists_from_spaces(
            client, workspace_id, space_ids, scan_size, archived
        )

    return []
