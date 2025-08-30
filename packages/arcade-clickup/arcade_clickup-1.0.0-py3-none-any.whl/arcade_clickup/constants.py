"""
ClickUp toolkit constants and configuration values.

This module contains all configurable constants used throughout the ClickUp toolkit,
providing a centralized location for configuration management.
"""

from enum import Enum

# ClickUp API Configuration
CLICKUP_API_BASE_URL = "https://api.clickup.com/api/v2"
CLICKUP_GUI_BASE_URL = "https://app.clickup.com"
CLICKUP_MAX_CONCURRENT_REQUESTS = 5

# Request Configuration
CLICKUP_REQUEST_TIMEOUT = 30.0

# Error Messages
ERROR_MESSAGES = {
    "no_auth_token": "No authentication token available",
    "invalid_workspace_id": "Invalid workspace ID format: '{workspace_id}'",
    "workspace_not_found": "Workspace with ID '{workspace_id}' not found or not accessible.",
    "json_parse_error": "Failed to parse JSON response: {error}",
    "request_failed": "Request failed: {error}",
}

# Developer Error Messages
DEVELOPER_ERROR_MESSAGES = {
    "workspace_validation": (
        "The workspace_id '{workspace_id}' is not in the expected format. "
        "ClickUp workspace IDs should be numeric strings. "
        "Please verify the workspace_id parameter."
    ),
    "workspace_not_found": (
        "The ClickUp API returned no workspace details for workspace_id '{workspace_id}'. "
        "This could indicate: 1) Invalid workspace ID, 2) Insufficient permissions, "
        "3) Workspace doesn't exist, or 4) API authentication issues."
    ),
}

# HTTP Status Code Messages
STATUS_CODE_MESSAGES = {
    401: "Authentication failed. Please check your ClickUp API token.",
    403: "Access denied. You don't have permission to access this resource.",
    404: "Resource not found. The requested workspace or resource doesn't exist.",
    429: "Rate limit exceeded. Please try again later.",
    500: "ClickUp server error. Please try again later.",
}

# Role Mapping
ROLE_MAPPING = {
    1: "admin",
    2: "member",
}


class TaskPriority(str, Enum):
    """
    ClickUp task priority label. This is a string enum suitable for tool inputs.

    Mapping to ClickUp API integer priorities (handled in code):
    - URGENT -> 1 (highest)
    - HIGH   -> 2
    - NORMAL -> 3
    - LOW    -> 4 (lowest)
    """

    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"


class TaskOrderBy(str, Enum):
    """
    ClickUp task ordering options for filtering and sorting results.

    These correspond to the order_by parameter values accepted by the
    ClickUp Get Filtered Team Tasks API endpoint.
    """

    CREATED = "created"
    UPDATED = "updated"
    DUE_DATE = "due_date"


class FilterScope(str, Enum):
    """
    Scope types for filtering tasks by organizational hierarchy.

    These define the level at which to filter tasks within ClickUp's
    organizational structure.
    """

    ALL = "all"
    SPACES = "spaces"
    FOLDERS = "folders"
    LISTS = "lists"


class CommentResolution(str, Enum):
    """
    Comment resolution status options for updating comments.

    These control whether a comment is marked as resolved or unresolved
    in ClickUp's comment system.
    """

    SET_AS_RESOLVED = "resolved"
    SET_AS_UNRESOLVED = "unresolved"


# Fuzzy Search Configuration
FUZZY_SEARCH_MIN_QUERY_LENGTH = 6
FUZZY_SEARCH_MIN_SCORE = 0.35
FUZZY_SEARCH_HIGH_QUALITY_THRESHOLD = 0.95
FUZZY_SEARCH_MIN_HIGH_QUALITY_MATCHES = 10
FUZZY_SEARCH_DEFAULT_SCAN_SIZE = 500  # Default number of items to scan
FUZZY_SEARCH_MAX_PAGES = 5  # Maximum pages to fetch (5 * 100 = 500 max)
FUZZY_SEARCH_MIN_RESULTS = 20  # Minimum results to return

# Fuzzy Search Scoring Constants
# Used in score_match() function in fuzzy_search_utils.py

# Word coverage scoring: score = base + A * query_coverage + B * text_coverage + any_match_bonus
# Used for unified word-level matching:
# coverage_score = FUZZY_LITE_WORD_BASE + FUZZY_LITE_WORD_A * query_coverage +
#                  FUZZY_LITE_WORD_B * text_coverage + FUZZY_LITE_WORD_ANY_MATCH_BONUS
FUZZY_LITE_WORD_BASE = 0.45  # Base score for word coverage matches
FUZZY_LITE_WORD_A = 0.22  # Weight for query coverage (how much of query is matched)
FUZZY_LITE_WORD_B = 0.08  # Weight for text coverage (how much of text is matched)
FUZZY_LITE_WORD_ANY_MATCH_BONUS = 0.02  # Small bonus for any word matches

# Substring match scoring: score = multiplier * (query_len / text_len)
# Used for direct substring matches:
# return FUZZY_SEARCH_SUBSTRING_MULTIPLIER * (len(query_lower) / len(text_lower))
FUZZY_SEARCH_SUBSTRING_MULTIPLIER = 0.9  # Multiplier for substring length ratio
FUZZY_SEARCH_SUBSTRING_MIN_LENGTH = 4  # Minimum query length for substring boosting
FUZZY_SEARCH_SUBSTRING_MIN_COVERAGE = 0.3  # Minimum coverage ratio for boosting (30%)
FUZZY_SEARCH_SUBSTRING_BOOST_SCORE = 0.4  # Minimum score for substantial substring matches

# Fuzzy matching scoring: score = base + (fuzzy_score - threshold) * multiplier
# Used for high fuzzy scores:
# return FUZZY_SEARCH_FUZZY_HIGH_BASE + (best_fuzzy - FUZZY_SEARCH_FUZZY_HIGH_THRESHOLD) *
#        FUZZY_SEARCH_FUZZY_HIGH_MULTIPLIER
FUZZY_SEARCH_FUZZY_HIGH_THRESHOLD = 0.7  # Threshold for high fuzzy scores
FUZZY_SEARCH_FUZZY_HIGH_BASE = 0.5  # Base score for high fuzzy matches
FUZZY_SEARCH_FUZZY_HIGH_MULTIPLIER = 0.5  # Multiplier for fuzzy score above threshold
FUZZY_SEARCH_FUZZY_LOW_MULTIPLIER = (
    0.5  # Multiplier for low fuzzy scores: return best_fuzzy * FUZZY_SEARCH_FUZZY_LOW_MULTIPLIER
)

# Score adjustment constants for filter_and_rank_matches()
# Used in filter_and_rank_matches() function in fuzzy_search_utils.py

# Generic name penalty: adjusted_score = score * penalty_multiplier (when score < threshold)
FUZZY_SEARCH_GENERIC_PENALTY_THRESHOLD = 0.5  # Score threshold for applying generic name penalty
FUZZY_SEARCH_GENERIC_PENALTY_MULTIPLIER = 0.5  # Penalty multiplier (cuts score in half)

# Descriptive name bonus: adjusted_score = min(1.0, score * bonus_multiplier)
FUZZY_SEARCH_DESCRIPTIVE_WORD_THRESHOLD = 3  # Minimum word count for descriptive bonus
FUZZY_SEARCH_DESCRIPTIVE_BONUS_MULTIPLIER = 1.1  # Bonus multiplier (10% increase)
