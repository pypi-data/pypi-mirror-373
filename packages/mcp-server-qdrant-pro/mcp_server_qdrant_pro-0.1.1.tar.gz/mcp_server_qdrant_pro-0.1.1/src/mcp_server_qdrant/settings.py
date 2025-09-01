from typing import Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings

from mcp_server_qdrant.embeddings.types import EmbeddingProviderType

DEFAULT_TOOL_STORE_DESCRIPTION = (
    "Keep the memory for later use, when you are asked to remember something."
)
DEFAULT_TOOL_FIND_DESCRIPTION = (
    "Look up memories in Qdrant. Use this tool when you need to: \n"
    " - Find memories by their content \n"
    " - Access memories for further analysis \n"
    " - Get some personal information about the user"
)

# Enterprise tool descriptions for GitHub codebase search
ENTERPRISE_TOOL_SEARCH_DESCRIPTION = (
    "Search for code patterns and implementations across GitHub repositories. "
    "Use this tool to find specific functionality, patterns, or implementations within a codebase. "
    "Always specify repository_id to scope your search to a specific repository. "
    "Use themes to find semantic patterns (e.g., 'authentication', 'database', 'api'). "
    "Examples:\n"
    "- Find authentication patterns: repository_id='owner/repo', themes=['authentication']\n"
    "- Find TypeScript database code: repository_id='owner/repo', themes=['database'], programming_language='typescript'\n"
    "- Find complex frontend components: repository_id='owner/repo', themes=['frontend'], complexity_score=5"
)

METADATA_PATH = "metadata"


class ToolSettings(BaseSettings):
    """
    Configuration for all the tools.
    """

    tool_store_description: str = Field(
        default=DEFAULT_TOOL_STORE_DESCRIPTION,
        validation_alias="TOOL_STORE_DESCRIPTION",
    )
    tool_find_description: str = Field(
        default=DEFAULT_TOOL_FIND_DESCRIPTION,
        validation_alias="TOOL_FIND_DESCRIPTION",
    )
    enterprise_mode: bool = Field(
        default=False,
        validation_alias="ENTERPRISE_MODE",
        description="Enable enterprise GitHub codebase search mode"
    )

    def get_effective_find_description(self) -> str:
        """Get the appropriate find tool description based on enterprise mode."""
        if self.enterprise_mode:
            return ENTERPRISE_TOOL_SEARCH_DESCRIPTION
        return self.tool_find_description


class EmbeddingProviderSettings(BaseSettings):
    """
    Configuration for the embedding provider.
    """

    provider_type: EmbeddingProviderType = Field(
        default=EmbeddingProviderType.FASTEMBED,
        validation_alias="EMBEDDING_PROVIDER",
    )
    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )


class FilterableField(BaseModel):
    name: str = Field(description="The name of the field payload field to filter on")
    description: str = Field(
        description="A description for the field used in the tool description"
    )
    field_type: Literal["keyword", "integer", "float", "boolean"] = Field(
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
    enterprise_mode: bool = Field(
        default=False,
        validation_alias="ENTERPRISE_MODE",
        description="Enable enterprise GitHub codebase search configuration"
    )

    def filterable_fields_dict(self) -> dict[str, FilterableField]:
        if self.enterprise_mode:
            return self._get_enterprise_filterable_fields_dict()
        if self.filterable_fields is None:
            return {}
        return {field.name: field for field in self.filterable_fields}

    def filterable_fields_dict_with_conditions(self) -> dict[str, FilterableField]:
        if self.enterprise_mode:
            return self._get_enterprise_filterable_fields_with_conditions()
        if self.filterable_fields is None:
            return {}
        return {
            field.name: field
            for field in self.filterable_fields
            if field.condition is not None
        }

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
