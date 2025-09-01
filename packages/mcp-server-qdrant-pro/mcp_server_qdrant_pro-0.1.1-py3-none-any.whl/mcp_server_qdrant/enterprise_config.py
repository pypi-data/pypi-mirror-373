"""
Enterprise configuration for GitHub codebase search.

This module provides predefined filterable field configurations optimized for
enterprise code search use cases, with hierarchical filtering that prioritizes
repository scoping and semantic theme matching.
"""

from mcp_server_qdrant.settings import FilterableField

# Enterprise Code Search Filterable Fields Configuration
# Hierarchical priority: repository_id (required) -> themes -> refinement filters
ENTERPRISE_FILTERABLE_FIELDS = [
    # PRIMARY FILTER - Repository Scoping (Always Required)
    FilterableField(
        name="repository_id",
        description="Repository identifier in format 'owner/repo' (e.g., 'taika-st/dtna-chat')",
        field_type="keyword",
        condition="==",
        required=True
    ),

    # SECONDARY FILTER - Semantic Content Classification
    FilterableField(
        name="themes",
        description="Code themes/patterns array - searches for any matching theme (e.g., 'authentication', 'database', 'frontend', 'api')",
        field_type="keyword",
        condition="any",  # Enables array matching with MatchAny
        required=False
    ),

    # TERTIARY FILTERS - File and Code Characteristics
    FilterableField(
        name="programming_language",
        description="Programming language (e.g., 'typescript', 'python', 'javascript', 'rust')",
        field_type="keyword",
        condition="==",
        required=False
    ),

    FilterableField(
        name="file_type",
        description="File extension/type (e.g., 'ts', 'py', 'js', 'md')",
        field_type="keyword",
        condition="==",
        required=False
    ),

    FilterableField(
        name="directory",
        description="Directory path within repository (e.g., 'src/lib/auth', 'components/ui')",
        field_type="keyword",
        condition="==",
        required=False
    ),

    FilterableField(
        name="file_name",
        description="Specific file name (e.g., 'schema.pg.ts', 'auth.py')",
        field_type="keyword",
        condition="==",
        required=False
    ),

    # CODE QUALITY AND COMPLEXITY FILTERS
    FilterableField(
        name="has_code_patterns",
        description="Whether file contains identifiable code patterns (true/false)",
        field_type="boolean",
        condition="==",
        required=False
    ),

    FilterableField(
        name="has_comments",
        description="Whether file contains comments (true/false)",
        field_type="boolean",
        condition="==",
        required=False
    ),

    FilterableField(
        name="complexity_score",
        description="Minimum code complexity score (integer, higher = more complex)",
        field_type="integer",
        condition=">=",
        required=False
    ),

    # SIZE AND SCOPE FILTERS
    FilterableField(
        name="size",
        description="Minimum file size in bytes",
        field_type="integer",
        condition=">=",
        required=False
    ),

    FilterableField(
        name="line_count",
        description="Minimum number of lines in the code chunk",
        field_type="integer",
        condition=">=",
        required=False
    ),

    FilterableField(
        name="word_count",
        description="Minimum word count in the code chunk",
        field_type="integer",
        condition=">=",
        required=False
    ),

    # VERSION CONTROL FILTERS
    FilterableField(
        name="branch",
        description="Git branch name (e.g., 'main', 'develop', 'feature/auth')",
        field_type="keyword",
        condition="==",
        required=False
    ),

    FilterableField(
        name="sha",
        description="Git commit SHA hash",
        field_type="keyword",
        condition="==",
        required=False
    ),

    # INDEX-ONLY FIELDS (indexed but not exposed as tool parameters)
    # These are useful for internal processing and future extensibility
    FilterableField(
        name="content_type",
        description="Content type classification (code, docs, config, etc.)",
        field_type="keyword",
        condition=None,  # Index only, no tool parameter
        required=False
    ),

    FilterableField(
        name="document_id",
        description="Unique document identifier",
        field_type="keyword",
        condition=None,  # Index only, no tool parameter
        required=False
    ),

    FilterableField(
        name="chunk_length",
        description="Length of the text chunk",
        field_type="integer",
        condition=None,  # Index only, no tool parameter
        required=False
    ),

    FilterableField(
        name="start_index",
        description="Starting position of chunk within file",
        field_type="integer",
        condition=None,  # Index only, no tool parameter
        required=False
    ),
]

# Enterprise Tool Descriptions
ENTERPRISE_TOOL_DESCRIPTIONS = {
    "search": (
        "Search for code patterns and implementations across GitHub repositories. "
        "Use this tool to find specific functionality, patterns, or implementations within a codebase. "
        "Always specify repository_id to scope your search to a specific repository. "
        "Use themes to find semantic patterns (e.g., 'authentication', 'database', 'api'). "
        "Examples:\n"
        "- Find authentication patterns: repository_id='owner/repo', themes=['authentication']\n"
        "- Find TypeScript database code: repository_id='owner/repo', themes=['database'], programming_language='typescript'\n"
        "- Find complex frontend components: repository_id='owner/repo', themes=['frontend'], complexity_score=5"
    ),

    "analyze_repository": (
        "Analyze code patterns and structure across an entire repository. "
        "This tool provides insights into the codebase architecture, common patterns, "
        "and technology usage within a specific repository."
    ),

    "find_implementations": (
        "Find all implementations of a specific pattern or functionality across repositories. "
        "Useful for discovering how certain features are implemented, comparing approaches, "
        "or finding code examples."
    )
}

# Convenience function to get filterable fields as dict
def get_enterprise_filterable_fields_dict() -> dict[str, FilterableField]:
    """Return enterprise filterable fields as a dictionary keyed by field name."""
    return {field.name: field for field in ENTERPRISE_FILTERABLE_FIELDS}

# Convenience function to get only fields with conditions (exposed to tools)
def get_enterprise_filterable_fields_with_conditions() -> dict[str, FilterableField]:
    """Return only enterprise filterable fields that have conditions (exposed as tool parameters)."""
    return {
        field.name: field
        for field in ENTERPRISE_FILTERABLE_FIELDS
        if field.condition is not None
    }
