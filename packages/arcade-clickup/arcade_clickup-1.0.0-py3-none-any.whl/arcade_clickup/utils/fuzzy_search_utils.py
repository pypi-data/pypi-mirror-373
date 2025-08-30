"""Shared fuzzy search utilities for ClickUp resources."""

from typing import Any

from rapidfuzz import fuzz

from arcade_clickup.constants import (
    FUZZY_LITE_WORD_A,
    FUZZY_LITE_WORD_ANY_MATCH_BONUS,
    FUZZY_LITE_WORD_B,
    FUZZY_LITE_WORD_BASE,
    FUZZY_SEARCH_DESCRIPTIVE_BONUS_MULTIPLIER,
    FUZZY_SEARCH_DESCRIPTIVE_WORD_THRESHOLD,
    FUZZY_SEARCH_FUZZY_HIGH_BASE,
    FUZZY_SEARCH_FUZZY_HIGH_MULTIPLIER,
    FUZZY_SEARCH_FUZZY_HIGH_THRESHOLD,
    FUZZY_SEARCH_FUZZY_LOW_MULTIPLIER,
    FUZZY_SEARCH_GENERIC_PENALTY_MULTIPLIER,
    FUZZY_SEARCH_GENERIC_PENALTY_THRESHOLD,
    FUZZY_SEARCH_HIGH_QUALITY_THRESHOLD,
    FUZZY_SEARCH_MIN_HIGH_QUALITY_MATCHES,
    FUZZY_SEARCH_MIN_RESULTS,
    FUZZY_SEARCH_MIN_SCORE,
    FUZZY_SEARCH_SUBSTRING_BOOST_SCORE,
    FUZZY_SEARCH_SUBSTRING_MIN_COVERAGE,
    FUZZY_SEARCH_SUBSTRING_MIN_LENGTH,
    FUZZY_SEARCH_SUBSTRING_MULTIPLIER,
)


def score_match(query: str, text: str) -> float:
    """
    Score a potential match between query and text using a simplified algorithm.

    The algorithm uses three scoring approaches and returns the highest score:
    1. Unified word coverage scoring
    2. Direct substring matching with smart boosting
    3. RapidFuzz fuzzy matching fallback

    Returns a score between 0.0 and 1.0, with higher scores for better matches.
    """
    query_lower = query.lower().strip()
    text_lower = text.lower().strip()

    if not query_lower or not text_lower:
        return 0.0

    # Exact match fast-path
    if query_lower == text_lower:
        return 1.0

    # 1. Unified word coverage scoring
    query_words = set(query_lower.split())
    text_words = set(text_lower.split())
    common = query_words & text_words
    coverage_score = 0.0

    if common:
        query_coverage = len(common) / len(query_words)
        text_coverage = len(common) / len(text_words)
        coverage_score = (
            FUZZY_LITE_WORD_BASE
            + FUZZY_LITE_WORD_A * query_coverage
            + FUZZY_LITE_WORD_B * text_coverage
            + FUZZY_LITE_WORD_ANY_MATCH_BONUS
        )

    # 2. Direct substring matching with smart boosting
    substring_score = 0.0
    if query_lower in text_lower:
        coverage_ratio = len(query_lower) / len(text_lower)

        # Smart boosting: only for substantial matches
        if (
            len(query_lower) >= FUZZY_SEARCH_SUBSTRING_MIN_LENGTH
            and coverage_ratio >= FUZZY_SEARCH_SUBSTRING_MIN_COVERAGE
        ):
            substring_score = FUZZY_SEARCH_SUBSTRING_BOOST_SCORE
        else:
            substring_score = FUZZY_SEARCH_SUBSTRING_MULTIPLIER * coverage_ratio

    # 3. RapidFuzz fuzzy matching (reduced metrics for performance)
    fuzzy_score = 0.0
    try:
        partial_ratio = fuzz.partial_ratio(query_lower, text_lower) / 100.0
        token_set_ratio = fuzz.token_set_ratio(query_lower, text_lower) / 100.0
        best_fuzzy = max(partial_ratio, token_set_ratio)

        if best_fuzzy >= FUZZY_SEARCH_FUZZY_HIGH_THRESHOLD:
            fuzzy_score = (
                FUZZY_SEARCH_FUZZY_HIGH_BASE
                + (best_fuzzy - FUZZY_SEARCH_FUZZY_HIGH_THRESHOLD)
                * FUZZY_SEARCH_FUZZY_HIGH_MULTIPLIER
            )
        else:
            fuzzy_score = best_fuzzy * FUZZY_SEARCH_FUZZY_LOW_MULTIPLIER
    except Exception:
        fuzzy_score = 0.0

    # Return the best score from all approaches
    return max(coverage_score, substring_score, fuzzy_score)


def filter_and_rank_matches(
    items: list[dict[str, Any]],
    query: str,
    name_field: str = "name",
    min_score: float = FUZZY_SEARCH_MIN_SCORE,
) -> list[tuple[dict[str, Any], float]]:
    """
    Filter and rank items by fuzzy matching their names against a query.

    Args:
        items: List of items to search through
        query: Search query string
        name_field: Field name containing the text to match against
        min_score: Minimum score threshold for matches

    Returns:
        List of tuples (item, score) sorted by relevance score (highest first)
    """
    matches_with_scores: list[tuple[dict[str, Any], float]] = []

    for item in items:
        name = item.get(name_field, "")
        if not name:
            continue

        score = score_match(query, name)

        # Apply penalties and bonuses to improve matching quality
        adjusted_score = score

        # Penalize very generic single-word names when they have low scores
        if (
            len(name.strip().split()) == 1
            and name.lower() in ["list", "project", "task", "item", "folder"]
            and score < FUZZY_SEARCH_GENERIC_PENALTY_THRESHOLD  # Only penalize if already low score
        ):
            adjusted_score = score * FUZZY_SEARCH_GENERIC_PENALTY_MULTIPLIER  # Cut score in half

        # Boost longer, more descriptive names
        word_count = len(name.strip().split())
        if word_count >= FUZZY_SEARCH_DESCRIPTIVE_WORD_THRESHOLD:
            adjusted_score = min(
                1.0, score * FUZZY_SEARCH_DESCRIPTIVE_BONUS_MULTIPLIER
            )  # 10% bonus, cap at 1.0

        if adjusted_score >= min_score:
            matches_with_scores.append((item, adjusted_score))

    # Sort by score (highest first), then by date_updated if available
    matches_with_scores.sort(
        key=lambda x: (
            x[1],  # Score
            int(x[0].get("date_updated", "0")) if x[0].get("date_updated") else 0,
        ),
        reverse=True,
    )

    return matches_with_scores


def should_continue_search(
    matches: list[dict[str, Any]],
    scores: list[float],
    pages_fetched: int,
    max_pages: int,
    is_last_page: bool,
) -> bool:
    """
    Determine if search should continue to fetch more pages.

    Uses a multi-phase approach:
    - Quick scan first 3 pages for high-quality matches
    - Deep scan if not enough high-quality matches found
    """
    if pages_fetched >= max_pages or is_last_page:
        return False

    # Count high-quality matches
    high_quality_count = sum(1 for score in scores if score >= FUZZY_SEARCH_HIGH_QUALITY_THRESHOLD)

    # Phase 1: Quick scan (first 3 pages)
    if pages_fetched < 3:
        # Continue quick scan unless we have enough high-quality matches
        return high_quality_count < FUZZY_SEARCH_MIN_HIGH_QUALITY_MATCHES

    # Phase 2: Deep scan decision
    # Continue if we don't have enough high-quality matches or minimum results
    return (
        high_quality_count < FUZZY_SEARCH_MIN_HIGH_QUALITY_MATCHES
        or len(matches) < FUZZY_SEARCH_MIN_RESULTS
    )
