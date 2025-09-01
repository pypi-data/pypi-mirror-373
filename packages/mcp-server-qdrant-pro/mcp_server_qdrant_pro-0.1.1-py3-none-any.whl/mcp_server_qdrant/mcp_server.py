import json
import logging
from typing import Annotated, Any, Optional

from fastmcp import Context, FastMCP
from pydantic import Field
from qdrant_client import models

from mcp_server_qdrant.common.filters import make_indexes
from mcp_server_qdrant.common.func_tools import make_partial_function
from mcp_server_qdrant.common.wrap_filters import wrap_filters
from mcp_server_qdrant.embeddings.base import EmbeddingProvider
from mcp_server_qdrant.embeddings.factory import create_embedding_provider
from mcp_server_qdrant.qdrant import ArbitraryFilter, Entry, Metadata, QdrantConnector
from mcp_server_qdrant.settings import (
    EmbeddingProviderSettings,
    QdrantSettings,
    ToolSettings,
)
from mcp_server_qdrant.enterprise_tools import (
    search_repository,
    analyze_repository_patterns,
    find_implementations,
)

logger = logging.getLogger(__name__)


# FastMCP is an alternative interface for declaring the capabilities
# of the server. Its API is based on FastAPI.
class QdrantMCPServer(FastMCP):
    """
    A MCP server for Qdrant.
    """

    def __init__(
        self,
        tool_settings: ToolSettings,
        qdrant_settings: QdrantSettings,
        embedding_provider_settings: Optional[EmbeddingProviderSettings] = None,
        embedding_provider: Optional[EmbeddingProvider] = None,
        name: str = "mcp-server-qdrant",
        instructions: str | None = None,
        **settings: Any,
    ):
        self.tool_settings = tool_settings
        self.qdrant_settings = qdrant_settings

        if embedding_provider_settings and embedding_provider:
            raise ValueError(
                "Cannot provide both embedding_provider_settings and embedding_provider"
            )

        if not embedding_provider_settings and not embedding_provider:
            raise ValueError(
                "Must provide either embedding_provider_settings or embedding_provider"
            )

        self.embedding_provider_settings: Optional[EmbeddingProviderSettings] = None
        self.embedding_provider: Optional[EmbeddingProvider] = None

        if embedding_provider_settings:
            self.embedding_provider_settings = embedding_provider_settings
            self.embedding_provider = create_embedding_provider(
                embedding_provider_settings
            )
        else:
            self.embedding_provider_settings = None
            self.embedding_provider = embedding_provider

        assert self.embedding_provider is not None, "Embedding provider is required"

        self.qdrant_connector = QdrantConnector(
            qdrant_settings.location,
            qdrant_settings.api_key,
            qdrant_settings.collection_name,
            self.embedding_provider,
            qdrant_settings.local_path,
            make_indexes(qdrant_settings.filterable_fields_dict()),
        )

        super().__init__(name=name, instructions=instructions, **settings)

        self.setup_tools()

    def format_entry(self, entry: Entry) -> str:
        """
        Feel free to override this method in your subclass to customize the format of the entry.
        """
        entry_metadata = json.dumps(entry.metadata) if entry.metadata else ""
        return f"<entry><content>{entry.content}</content><metadata>{entry_metadata}</metadata></entry>"

    def setup_tools(self):
        """
        Register the tools in the server.
        """

        async def store(
            ctx: Context,
            information: Annotated[str, Field(description="Text to store")],
            collection_name: Annotated[
                str, Field(description="The collection to store the information in")
            ],
            # The `metadata` parameter is defined as non-optional, but it can be None.
            # If we set it to be optional, some of the MCP clients, like Cursor, cannot
            # handle the optional parameter correctly.
            metadata: Annotated[
                Metadata | None,
                Field(
                    description="Extra metadata stored along with memorised information. Any json is accepted."
                ),
            ] = None,
        ) -> str:
            """
            Store some information in Qdrant.
            :param ctx: The context for the request.
            :param information: The information to store.
            :param metadata: JSON metadata to store with the information, optional.
            :param collection_name: The name of the collection to store the information in, optional. If not provided,
                                    the default collection is used.
            :return: A message indicating that the information was stored.
            """
            await ctx.debug(f"Storing information {information} in Qdrant")

            entry = Entry(content=information, metadata=metadata)

            await self.qdrant_connector.store(entry, collection_name=collection_name)
            if collection_name:
                return f"Remembered: {information} in collection {collection_name}"
            return f"Remembered: {information}"

        async def find(
            ctx: Context,
            query: Annotated[str, Field(description="What to search for")],
            collection_name: Annotated[
                str, Field(description="The collection to search in")
            ],
            query_filter: ArbitraryFilter | None = None,
        ) -> list[str] | None:
            """
            Find memories in Qdrant.
            :param ctx: The context for the request.
            :param query: The query to use for the search.
            :param collection_name: The name of the collection to search in, optional. If not provided,
                                    the default collection is used.
            :param query_filter: The filter to apply to the query.
            :return: A list of entries found or None.
            """

            # Log query_filter
            await ctx.debug(f"Query filter: {query_filter}")

            query_filter = models.Filter(**query_filter) if query_filter else None

            await ctx.debug(f"Finding results for query {query}")

            entries = await self.qdrant_connector.search(
                query,
                collection_name=collection_name or self.qdrant_settings.collection_name,
                limit=limit or self.qdrant_settings.search_limit,
                query_filter=models.Filter(**query_filter) if query_filter else None,
            )
            if not entries:
                return None
            content = [
                f"Results for the query '{query}'",
            ]
            for entry in entries:
                content.append(self.format_entry(entry))
            return content

        find_foo = find
        store_foo = store

        filterable_conditions = (
            self.qdrant_settings.filterable_fields_dict_with_conditions()
        )

        if len(filterable_conditions) > 0:
            find_foo = wrap_filters(find_foo, filterable_conditions)
        elif not self.qdrant_settings.allow_arbitrary_filter:
            find_foo = make_partial_function(find_foo, {"query_filter": None})

        if self.qdrant_settings.collection_name:
            find_foo = make_partial_function(
                find_foo, {"collection_name": self.qdrant_settings.collection_name}
            )
            store_foo = make_partial_function(
                store_foo, {"collection_name": self.qdrant_settings.collection_name}
            )

        self.tool(
            find_foo,
            name="qdrant-find",
            description=self.tool_settings.get_effective_find_description(),
        )

        if not self.qdrant_settings.read_only:
            # Those methods can modify the database
            self.tool(
                store_foo,
                name="qdrant-store",
                description=self.tool_settings.tool_store_description,
            )

        # Register enterprise tools if enterprise mode is enabled
        if self.qdrant_settings.enterprise_mode:
            self.setup_enterprise_tools()

    def _parse_themes_json(self, themes: str | None) -> list[str] | None:
        """
        Parse themes from JSON string to list.

        :param themes: JSON string representation of themes array
        :return: List of themes or None
        :raises ValueError: If themes is not a valid JSON array
        """
        if not themes:
            return None

        try:
            import json
            themes_list = json.loads(themes)
            if not isinstance(themes_list, list):
                raise ValueError("themes must be a JSON array")
            return themes_list
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid themes format: {e}. Expected JSON array like '[\"auth\", \"db\"]'")

    def setup_enterprise_tools(self):
        """
        Register enterprise-specific tools for GitHub codebase search.
        """
        filterable_conditions = self.qdrant_settings.filterable_fields_dict_with_conditions()

        # Create enterprise tool functions with proper context
        async def enterprise_search_repository(
            ctx: Context,
            repository_id: str,
            query: str,
            themes: str | None = None,
            programming_language: str | None = None,
            complexity_score: int | None = None,
            file_type: str | None = None,
            directory: str | None = None,
            has_code_patterns: bool | None = None,
            query_filter: ArbitraryFilter | None = None,
        ):
            # Parse themes JSON string to list
            try:
                themes_list = self._parse_themes_json(themes)
            except ValueError as e:
                await ctx.error(str(e))
                return [f"Error: {e}"]

            # Build filter conditions from parameters
            filter_conditions: Dict[str, Any] = {"repository_id": repository_id}
            if themes_list:
                filter_conditions["themes"] = themes_list
            if programming_language:
                filter_conditions["programming_language"] = programming_language
            if complexity_score is not None:
                filter_conditions["complexity_score"] = complexity_score
            if file_type:
                filter_conditions["file_type"] = file_type
            if directory:
                filter_conditions["directory"] = directory
            if has_code_patterns is not None:
                filter_conditions["has_code_patterns"] = has_code_patterns

            # Build Qdrant filter
            from mcp_server_qdrant.common.filters import make_filter
            built_filter = make_filter(filterable_conditions, filter_conditions)
            combined_filter = models.Filter(**built_filter) if built_filter else None

            # Combine with any additional query filter
            if query_filter and combined_filter:
                additional_filter = models.Filter(**query_filter)
                # Ensure we have lists before concatenating
                must_conditions = []
                must_not_conditions = []

                # Handle combined_filter.must
                if combined_filter.must is not None:
                    if isinstance(combined_filter.must, list):
                        must_conditions.extend(combined_filter.must)
                    else:
                        must_conditions.append(combined_filter.must)

                # Handle additional_filter.must
                if additional_filter.must is not None:
                    if isinstance(additional_filter.must, list):
                        must_conditions.extend(additional_filter.must)
                    else:
                        must_conditions.append(additional_filter.must)

                # Handle combined_filter.must_not
                if combined_filter.must_not is not None:
                    if isinstance(combined_filter.must_not, list):
                        must_not_conditions.extend(combined_filter.must_not)
                    else:
                        must_not_conditions.append(combined_filter.must_not)

                # Handle additional_filter.must_not
                if additional_filter.must_not is not None:
                    if isinstance(additional_filter.must_not, list):
                        must_not_conditions.extend(additional_filter.must_not)
                    else:
                        must_not_conditions.append(additional_filter.must_not)

                combined_filter = models.Filter(
                    must=must_conditions if must_conditions else None,
                    must_not=must_not_conditions if must_not_conditions else None
                )
            elif query_filter:
                combined_filter = models.Filter(**query_filter)

            return await search_repository(
                ctx,
                self.qdrant_connector,
                self.qdrant_settings.search_limit,
                filterable_conditions,
                repository_id,
                query,
                self.qdrant_settings.collection_name,
                combined_filter.model_dump() if combined_filter else None,
            )

        async def enterprise_analyze_patterns(
            ctx: Context,
            repository_id: str,
            themes: str | None = None,
            programming_language: str | None = None,
            directory: str | None = None,
        ):
            # Parse themes JSON string to list
            try:
                themes_list = self._parse_themes_json(themes)
            except ValueError as e:
                await ctx.error(str(e))
                return [f"Error: {e}"]
            return await analyze_repository_patterns(
                ctx,
                self.qdrant_connector,
                self.qdrant_settings.search_limit,
                filterable_conditions,
                repository_id,
                self.qdrant_settings.collection_name or "qdrant_collection",
                themes_list,
                programming_language,
                directory,
            )

        async def enterprise_find_implementations(
            ctx: Context,
            repository_id: str,
            pattern_query: str,
            themes: str | None = None,
            programming_language: str | None = None,
            min_complexity: int | None = None,
        ):
            # Parse themes JSON string to list
            try:
                themes_list = self._parse_themes_json(themes)
            except ValueError as e:
                await ctx.error(str(e))
                return [f"Error: {e}"]
            return await find_implementations(
                ctx,
                self.qdrant_connector,
                self.qdrant_settings.search_limit,
                filterable_conditions,
                repository_id,
                pattern_query,
                self.qdrant_settings.collection_name or "qdrant_collection",
                themes_list,
                programming_language,
                min_complexity,
            )

        # Register enterprise tools directly (filter wrapping disabled for now)
        # Note: Individual parameters will be exposed based on function signatures

        # Apply query_filter removal if arbitrary filters not allowed
        if not self.qdrant_settings.allow_arbitrary_filter:
            enterprise_search_repository = make_partial_function(enterprise_search_repository, {"query_filter": None})

        # Register enterprise tools
        self.tool(
            enterprise_search_repository,
            name="qdrant-search-repository",
            description="Search for code patterns and implementations within a specific GitHub repository. "
                        "Always specify repository_id to scope your search. Use themes to find semantic patterns. "
                        "Examples: Find authentication code, database implementations, API endpoints."
        )

        self.tool(
            enterprise_analyze_patterns,
            name="qdrant-analyze-patterns",
            description="Analyze code patterns, themes, and architecture within a repository. "
                        "Provides insights into codebase structure, common patterns, and technology usage. "
                        "Useful for understanding unfamiliar codebases or documenting existing ones."
        )

        self.tool(
            enterprise_find_implementations,
            name="qdrant-find-implementations",
            description="Find all implementations of a specific pattern or functionality within a repository. "
                        "Useful for discovering how features are implemented, comparing approaches, "
                        "or finding examples of specific patterns. Returns implementations ranked by similarity."
        )
