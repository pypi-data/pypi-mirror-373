"""
ClickUp API response and tool output models using TypedDict.

This module contains all TypedDict definitions for:
- ClickUp API response structures
- Tool output models
- Shared data structures
"""

from .api_models import (
    ClickupFolder,
    ClickupList,
    ClickupMember,
    ClickupSpace,
    ClickupUser,
    ClickupWorkspace,
    FoldersResponse,
    ListsResponse,
    MembersResponse,
    SpacesResponse,
    WorkspacesResponse,
)
from .tool_models import (
    GetFoldersResult,
    GetListsResult,
    GetSpacesResult,
    GetTeamMembersResult,
    ToolError,
    ToolFolder,
    ToolList,
    ToolMember,
    ToolSpace,
    ToolWorkspace,
)

__all__ = [
    # API Models
    "ClickupFolder",
    "ClickupList",
    "ClickupMember",
    "ClickupSpace",
    "ClickupUser",
    "ClickupWorkspace",
    "FoldersResponse",
    "ListsResponse",
    "MembersResponse",
    "SpacesResponse",
    "WorkspacesResponse",
    # Tool Models
    "GetFoldersResult",
    "GetListsResult",
    "GetSpacesResult",
    "GetTeamMembersResult",
    "GetWorkspacesResult",
    "ToolError",
    "ToolFolder",
    "ToolList",
    "ToolMember",
    "ToolSpace",
    "ToolWorkspace",
]
