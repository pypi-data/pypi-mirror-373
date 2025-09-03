from typing import Literal

from pydantic import BaseModel, Field, model_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

from mcp_server_qdrant.embeddings.types import EmbeddingProviderType

# Back-compat defaults for generic tools (used by legacy tests)
DEFAULT_TOOL_STORE_DESCRIPTION = (
    "Store a document or text in the vector database with optional metadata."
)
DEFAULT_TOOL_FIND_DESCRIPTION = (
    "Find relevant entries in the vector database using a semantic query and optional filters."
)

# Enterprise tool descriptions for GitHub codebase search
SEARCH_REPOSITORY_DESCRIPTION = (
    "Search for code patterns and implementations within a specific GitHub repository. "
    "Use this tool to find specific functionality, patterns, or implementations within a codebase. "
    "Always specify repository_id to scope your search to a specific repository. "
    "Use themes to find semantic patterns (e.g., 'authentication', 'database', 'api'). "
    "Examples:\n"
    "- Find authentication patterns: repository_id='owner/repo', themes='[\"authentication\"]'\n"
    "- Find TypeScript database code: repository_id='owner/repo', themes='[\"database\"]', programming_language='typescript'\n"
    "- Find complex frontend components: repository_id='owner/repo', themes='[\"frontend\"]', complexity_score=5"
)

ANALYZE_PATTERNS_DESCRIPTION = (
    "Analyze code patterns, themes, and architecture within a repository. "
    "Provides insights into codebase structure, common patterns, and technology usage. "
    "Useful for understanding unfamiliar codebases or documenting existing ones."
)

FIND_IMPLEMENTATIONS_DESCRIPTION = (
    "Find all implementations of a specific pattern or functionality within a repository. "
    "Useful for discovering how features are implemented, comparing approaches, "
    "or finding examples of specific patterns. Returns implementations ranked by similarity."
)

METADATA_PATH = "metadata"


class ToolSettings(BaseSettings):
    """
    Configuration for enterprise GitHub codebase search tools.
    """

    # Legacy/generic tool descriptions (for tests/backward compatibility)
    tool_store_description: str = Field(
        default=DEFAULT_TOOL_STORE_DESCRIPTION,
        validation_alias="TOOL_STORE_DESCRIPTION",
    )
    tool_find_description: str = Field(
        default=DEFAULT_TOOL_FIND_DESCRIPTION,
        validation_alias="TOOL_FIND_DESCRIPTION",
    )

    search_repository_description: str = Field(
        default=SEARCH_REPOSITORY_DESCRIPTION,
        validation_alias="TOOL_SEARCH_REPOSITORY_DESCRIPTION",
    )
    analyze_patterns_description: str = Field(
        default=ANALYZE_PATTERNS_DESCRIPTION,
        validation_alias="TOOL_ANALYZE_PATTERNS_DESCRIPTION",
    )
    find_implementations_description: str = Field(
        default=FIND_IMPLEMENTATIONS_DESCRIPTION,
        validation_alias="TOOL_FIND_IMPLEMENTATIONS_DESCRIPTION",
    )

class EmbeddingProviderSettings(BaseSettings):
    """
    Configuration for the embedding provider.
    """

    # Allow extra to support legacy constructor kwargs in tests
    model_config = SettingsConfigDict(extra="allow")

    provider_type: EmbeddingProviderType | str = Field(
        default=EmbeddingProviderType.FASTEMBED,
        validation_alias=AliasChoices("EMBEDDING_PROVIDER", "provider"),
    )
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias=AliasChoices("EMBEDDING_MODEL", "model"),
    )

    @model_validator(mode="after")
    def _coerce_provider_type(self) -> "EmbeddingProviderSettings":
        """Coerce arbitrary provider inputs to a supported enum, defaulting to FASTEMBED.
        Accepts legacy strings like provider="test" used in tests without raising.
        """
        try:
            if isinstance(self.provider_type, str):
                normalized = self.provider_type.strip().lower()
                try:
                    self.provider_type = EmbeddingProviderType(normalized)
                except Exception:
                    self.provider_type = EmbeddingProviderType.FASTEMBED
        except Exception:
            self.provider_type = EmbeddingProviderType.FASTEMBED
        return self


class FilterableField(BaseModel):
    name: str = Field(description="The name of the field payload field to filter on")
    description: str = Field(
        description="A description for the field used in the tool description"
    )
    field_type: Literal["keyword", "integer", "float", "boolean", "text"] = Field(
        description="The type of the field"
    )
    condition: Literal["==", "!=", ">", ">=", "<", "<=", "any", "except"] | None = (
        Field(
            default=None,
            description=(
                "The condition to use for the filter. If not provided, the field will be indexed, but no "
                "filter argument will be exposed to MCP tool."
            ),
        )
    )
    required: bool = Field(
        default=False,
        description="Whether the field is required for the filter.",
    )


class QdrantSettings(BaseSettings):
    """
    Configuration for the Qdrant connector.
    """

    # Allow extra to maintain backward compatibility with various env inputs
    model_config = SettingsConfigDict(extra="allow")

    location: str | None = Field(default=None, validation_alias="QDRANT_URL")
    api_key: str | None = Field(default=None, validation_alias="QDRANT_API_KEY")
    collection_name: str | None = Field(
        default=None, validation_alias="COLLECTION_NAME"
    )
    local_path: str | None = Field(default=None, validation_alias="QDRANT_LOCAL_PATH")
    search_limit: int = Field(default=10, validation_alias="QDRANT_SEARCH_LIMIT")
    read_only: bool = Field(default=False, validation_alias="QDRANT_READ_ONLY")

    filterable_fields: list[FilterableField] | None = Field(default=None)

    allow_arbitrary_filter: bool = Field(
        default=False, validation_alias="QDRANT_ALLOW_ARBITRARY_FILTER"
    )

    def filterable_fields_dict(self) -> dict[str, FilterableField]:
        return self._get_enterprise_filterable_fields_dict()


    def filterable_fields_dict_with_conditions(self) -> dict[str, FilterableField]:
        return self._get_enterprise_filterable_fields_with_conditions()


    def _get_enterprise_filterable_fields_dict(self) -> dict[str, FilterableField]:
        """Get enterprise filterable fields configuration."""
        # Import here to avoid circular imports
        try:
            from mcp_server_qdrant.enterprise_config import get_enterprise_filterable_fields_dict
            return get_enterprise_filterable_fields_dict()
        except ImportError:
            # Fallback to empty dict if enterprise config is not available
            return {}

    def _get_enterprise_filterable_fields_with_conditions(self) -> dict[str, FilterableField]:
        """Get enterprise filterable fields with conditions."""
        # Import here to avoid circular imports
        try:
            from mcp_server_qdrant.enterprise_config import get_enterprise_filterable_fields_with_conditions
            return get_enterprise_filterable_fields_with_conditions()
        except ImportError:
            # Fallback to empty dict if enterprise config is not available
            return {}

    @model_validator(mode="after")
    def check_local_path_conflict(self) -> "QdrantSettings":
        if self.local_path:
            if self.location is not None or self.api_key is not None:
                raise ValueError(
                    "If 'local_path' is set, 'location' and 'api_key' must be None."
                )
        return self
