"""
Enterprise tools for GitHub codebase search.

This module provides MCP tools specifically designed for enterprise code search
use cases, with repository-scoped semantic search and code pattern analysis.
"""

import logging
from typing import Annotated, Any, Dict, List, Optional
from collections import Counter

from fastmcp import Context
from pydantic import Field
from qdrant_client import models

from mcp_server_qdrant.qdrant import QdrantConnector, Entry, ArbitraryFilter

logger = logging.getLogger(__name__)


def _ensure_condition_list(condition: models.Condition | List[models.Condition] | None) -> List[models.Condition]:
    """
    Convert a condition or list of conditions to a list.

    :param condition: Single condition, list of conditions, or None
    :return: List of conditions (empty if None)
    """
    if condition is None:
        return []
    elif isinstance(condition, list):
        return condition
    else:
        return [condition]


def _merge_filters(filter1: models.Filter | None, filter2: models.Filter | None) -> models.Filter | None:
    """
    Merge two filters, combining their must and must_not conditions.

    :param filter1: First filter (can be None)
    :param filter2: Second filter (can be None)
    :return: Merged filter or None if both inputs are None
    """
    if filter1 is None and filter2 is None:
        return None
    elif filter1 is None:
        return filter2
    elif filter2 is None:
        return filter1

    # Both filters exist, merge them
    must_conditions = _ensure_condition_list(filter1.must) + _ensure_condition_list(filter2.must)
    must_not_conditions = _ensure_condition_list(filter1.must_not) + _ensure_condition_list(filter2.must_not)

    return models.Filter(
        must=must_conditions if must_conditions else None,
        must_not=must_not_conditions if must_not_conditions else None
    )


def format_code_entry(entry: Entry, repository_id: str) -> str:
    """
    Format a code entry for enterprise display with rich metadata.

    :param entry: The entry to format
    :param repository_id: Repository identifier for context
    :return: Formatted string representation
    """
    if not entry.metadata:
        return f"<code_snippet><content>{entry.content}</content><repository>{repository_id}</repository></code_snippet>"

    metadata = entry.metadata

    # Extract key metadata fields
    file_path = metadata.get('file_path', 'Unknown file')
    programming_language = metadata.get('programming_language', 'Unknown')
    themes = metadata.get('themes', [])
    complexity_score = metadata.get('complexity_score', 0)
    line_count = metadata.get('line_count', 0)
    has_code_patterns = metadata.get('has_code_patterns', False)
    branch = metadata.get('branch', 'main')

    themes_str = ', '.join(themes) if themes else 'None'

    formatted = f"""<code_snippet>
<repository>{repository_id}</repository>
<file_path>{file_path}</file_path>
<programming_language>{programming_language}</programming_language>
<branch>{branch}</branch>
<themes>{themes_str}</themes>
<complexity_score>{complexity_score}</complexity_score>
<line_count>{line_count}</line_count>
<has_patterns>{has_code_patterns}</has_patterns>
<content>
{entry.content}
</content>
</code_snippet>"""

    return formatted


async def search_repository(
    ctx: Context,
    qdrant_connector: QdrantConnector,
    search_limit: int,
    filterable_fields_with_conditions: Dict[str, Any],
    repository_id: Annotated[str, Field(description="Repository identifier in format 'owner/repo' (e.g., 'taika-st/dtna-chat')")],
    query: Annotated[str, Field(description="Semantic search query for finding code patterns, functionality, or implementations")],
    collection_name: str,
    query_filter: ArbitraryFilter | None = None,
) -> List[str]:
    """
    Search for code patterns and implementations within a specific GitHub repository.

    This is the primary enterprise search tool for finding specific functionality,
    patterns, or implementations within a codebase. Always scoped to a single repository
    for focused, relevant results.

    :param ctx: The context for the request
    :param qdrant_connector: Qdrant connector instance
    :param search_limit: Maximum number of results to return
    :param filterable_fields_with_conditions: Available filterable fields configuration
    :param repository_id: Repository identifier (required)
    :param query: Semantic search query
    :param collection_name: Collection to search in
    :param query_filter: Additional filter conditions
    :param filter_kwargs: Additional filter parameters
    :return: List of formatted code snippets with metadata
    """

    await ctx.debug(f"Searching repository {repository_id} for query: {query}")

    # Build filter ensuring repository_id is always included
    filter_conditions: Dict[str, Any] = {"repository_id": repository_id}

    await ctx.debug(f"Applied filters: {filter_conditions}")

    # Build Qdrant filter
    from mcp_server_qdrant.common.filters import make_filter
    built_filter = make_filter(filterable_fields_with_conditions, filter_conditions)
    combined_filter = models.Filter(**built_filter) if built_filter else None

    # Combine with any additional query filter
    if query_filter:
        additional_filter = models.Filter(**query_filter)
        combined_filter = _merge_filters(combined_filter, additional_filter)

    # Execute search
    entries = await qdrant_connector.search(
        query,
        collection_name=collection_name,
        limit=search_limit,
        query_filter=combined_filter,
    )

    if not entries:
        return [f"No results found in repository '{repository_id}' for query '{query}'"]

    # Format results
    result = [f"Found {len(entries)} code snippets in repository '{repository_id}' for query '{query}':"]

    for entry in entries:
        formatted_entry = format_code_entry(entry, repository_id)
        result.append(formatted_entry)

    return result


async def analyze_repository_patterns(
    ctx: Context,
    qdrant_connector: QdrantConnector,
    search_limit: int,
    filterable_fields_with_conditions: Dict[str, Any],
    repository_id: Annotated[str, Field(description="Repository identifier in format 'owner/repo'")],
    collection_name: str,
    themes: Annotated[Optional[List[str]], Field(description="Specific themes to analyze (e.g., ['authentication', 'database'])")] = None,
    programming_language: Annotated[Optional[str], Field(description="Focus analysis on specific programming language")] = None,
    directory: Annotated[Optional[str], Field(description="Analyze specific directory within repository")] = None,
) -> List[str]:
    """
    Analyze code patterns, themes, and architecture within a repository.

    Provides insights into codebase structure, common patterns, technology usage,
    and architectural decisions. Useful for understanding unfamiliar codebases
    or documenting existing ones.

    :param ctx: The context for the request
    :param qdrant_connector: Qdrant connector instance
    :param search_limit: Maximum number of entries to analyze
    :param filterable_fields_with_conditions: Available filterable fields
    :param repository_id: Repository to analyze
    :param collection_name: Collection to search in
    :param themes: Specific themes to focus on
    :param programming_language: Language to focus analysis on
    :param directory: Directory to analyze
    :param filter_kwargs: Additional filter parameters
    :return: Analysis summary with statistics and insights
    """

    await ctx.debug(f"Analyzing patterns in repository {repository_id}")

    # Build base filter with repository scope
    filter_conditions: Dict[str, Any] = {"repository_id": repository_id}

    # Add optional filters
    if themes:
        filter_conditions["themes"] = themes
    if programming_language:
        filter_conditions["programming_language"] = programming_language
    if directory:
        filter_conditions["directory"] = directory

    await ctx.debug(f"Analysis filters: {filter_conditions}")

    # Build filter
    from mcp_server_qdrant.common.filters import make_filter
    built_filter = make_filter(filterable_fields_with_conditions, filter_conditions)
    query_filter = models.Filter(**built_filter) if built_filter else None

    # Use broad semantic query to get representative sample
    analysis_query = "code implementation function class method"
    if themes:
        analysis_query = f"{' '.join(themes)} {analysis_query}"

    # Execute search with larger limit for analysis
    analysis_limit = min(search_limit * 3, 100)  # Analyze more entries for better insights
    entries = await qdrant_connector.search(
        analysis_query,
        collection_name=collection_name,
        limit=analysis_limit,
        query_filter=query_filter,
    )

    if not entries:
        return [f"No code found in repository '{repository_id}' matching the specified criteria"]

    # Perform analysis
    analysis_results = _analyze_code_patterns(entries, repository_id)

    return analysis_results


async def find_implementations(
    ctx: Context,
    qdrant_connector: QdrantConnector,
    search_limit: int,
    filterable_fields_with_conditions: Dict[str, Any],
    repository_id: Annotated[str, Field(description="Repository identifier in format 'owner/repo'")],
    pattern_query: Annotated[str, Field(description="Description of the pattern or functionality to find (e.g., 'user authentication', 'database connection', 'API endpoints')")],
    collection_name: str,
    themes: Annotated[Optional[List[str]], Field(description="Expected themes for the pattern")] = None,
    programming_language: Annotated[Optional[str], Field(description="Expected programming language")] = None,
    min_complexity: Annotated[Optional[int], Field(description="Minimum complexity score for implementations")] = None,
) -> List[str]:
    """
    Find all implementations of a specific pattern or functionality within a repository.

    Useful for discovering how certain features are implemented, comparing different
    approaches, or finding examples of specific patterns. Returns implementations
    ranked by semantic similarity to the pattern query.

    :param ctx: The context for the request
    :param qdrant_connector: Qdrant connector instance
    :param search_limit: Maximum number of implementations to return
    :param filterable_fields_with_conditions: Available filterable fields
    :param repository_id: Repository to search in
    :param pattern_query: Description of what to find
    :param collection_name: Collection to search in
    :param themes: Expected themes for filtering
    :param programming_language: Expected language
    :param min_complexity: Minimum complexity threshold
    :param filter_kwargs: Additional filter parameters
    :return: List of implementations with similarity context
    """

    await ctx.debug(f"Finding implementations of '{pattern_query}' in repository {repository_id}")

    # Build filter
    filter_conditions: Dict[str, Any] = {"repository_id": repository_id}

    if themes:
        filter_conditions["themes"] = themes
    if programming_language:
        filter_conditions["programming_language"] = programming_language
    if min_complexity is not None:
        filter_conditions["complexity_score"] = min_complexity

    await ctx.debug(f"Implementation search filters: {filter_conditions}")

    # Build Qdrant filter
    from mcp_server_qdrant.common.filters import make_filter
    built_filter = make_filter(filterable_fields_with_conditions, filter_conditions)
    query_filter = models.Filter(**built_filter) if built_filter else None

    # Execute search
    entries = await qdrant_connector.search(
        pattern_query,
        collection_name=collection_name,
        limit=search_limit,
        query_filter=query_filter,
    )

    if not entries:
        return [f"No implementations found for pattern '{pattern_query}' in repository '{repository_id}'"]

    # Format results with implementation context
    result = [f"Found {len(entries)} implementations of '{pattern_query}' in repository '{repository_id}':"]

    for i, entry in enumerate(entries, 1):
        implementation_context = _extract_implementation_context(entry)
        formatted_entry = f"""<implementation rank="{i}">
{implementation_context}
{format_code_entry(entry, repository_id)}
</implementation>"""
        result.append(formatted_entry)

    return result


def _analyze_code_patterns(entries: List[Entry], repository_id: str) -> List[str]:
    """
    Analyze code patterns from a list of entries and generate insights.

    :param entries: List of code entries to analyze
    :param repository_id: Repository identifier for context
    :return: Analysis results as formatted strings
    """

    if not entries:
        return [f"No code entries available for analysis in repository '{repository_id}'"]

    # Collect statistics
    languages = Counter()
    themes = Counter()
    directories = Counter()
    complexity_scores = []
    file_types = Counter()
    has_patterns_count = 0
    has_comments_count = 0
    total_lines = 0

    for entry in entries:
        if not entry.metadata:
            continue

        metadata = entry.metadata

        # Language analysis
        lang = metadata.get('programming_language', 'unknown')
        languages[lang] += 1

        # Theme analysis
        entry_themes = metadata.get('themes', [])
        for theme in entry_themes:
            themes[theme] += 1

        # Directory analysis
        directory = metadata.get('directory', 'root')
        directories[directory] += 1

        # File type analysis
        file_type = metadata.get('file_type', 'unknown')
        file_types[file_type] += 1

        # Complexity analysis
        complexity = metadata.get('complexity_score', 0)
        complexity_scores.append(complexity)

        # Pattern and comment analysis
        if metadata.get('has_code_patterns', False):
            has_patterns_count += 1
        if metadata.get('has_comments', False):
            has_comments_count += 1

        # Size analysis
        lines = metadata.get('line_count', 0)
        total_lines += lines

    # Generate analysis report
    total_entries = len(entries)
    avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 0
    avg_lines = total_lines / total_entries if total_entries > 0 else 0

    analysis = [
        f"## Repository Pattern Analysis: {repository_id}",
        f"**Analyzed {total_entries} code entries**",
        "",
        "### Programming Languages",
    ]

    for lang, count in languages.most_common(5):
        percentage = (count / total_entries) * 100
        analysis.append(f"- {lang}: {count} files ({percentage:.1f}%)")

    analysis.extend([
        "",
        "### Code Themes & Patterns",
    ])

    for theme, count in themes.most_common(10):
        percentage = (count / total_entries) * 100
        analysis.append(f"- {theme}: {count} occurrences ({percentage:.1f}%)")

    analysis.extend([
        "",
        "### Directory Distribution",
    ])

    for directory, count in directories.most_common(8):
        percentage = (count / total_entries) * 100
        analysis.append(f"- {directory}: {count} files ({percentage:.1f}%)")

    analysis.extend([
        "",
        "### Code Quality Metrics",
        f"- Average complexity score: {avg_complexity:.1f}",
        f"- Average lines per chunk: {avg_lines:.1f}",
        f"- Files with code patterns: {has_patterns_count} ({(has_patterns_count/total_entries)*100:.1f}%)",
        f"- Files with comments: {has_comments_count} ({(has_comments_count/total_entries)*100:.1f}%)",
        "",
        "### File Types",
    ])

    for file_type, count in file_types.most_common(8):
        percentage = (count / total_entries) * 100
        analysis.append(f"- {file_type}: {count} files ({percentage:.1f}%)")

    return analysis


def _extract_implementation_context(entry: Entry) -> str:
    """
    Extract contextual information about an implementation from its metadata.

    :param entry: Code entry to extract context from
    :return: Formatted context string
    """

    if not entry.metadata:
        return "<context>No metadata available</context>"

    metadata = entry.metadata

    # Key contextual elements
    file_path = metadata.get('file_path', 'Unknown location')
    themes = metadata.get('themes', [])
    complexity = metadata.get('complexity_score', 0)
    lines = metadata.get('line_count', 0)
    has_patterns = metadata.get('has_code_patterns', False)

    themes_str = ', '.join(themes) if themes else 'None identified'

    context = f"""<context>
<location>{file_path}</location>
<themes>{themes_str}</themes>
<complexity>{complexity}</complexity>
<lines>{lines}</lines>
<structured_patterns>{'Yes' if has_patterns else 'No'}</structured_patterns>
</context>"""

    return context
