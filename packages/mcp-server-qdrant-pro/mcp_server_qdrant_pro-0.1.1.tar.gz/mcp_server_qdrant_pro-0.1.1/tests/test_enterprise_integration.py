"""
Integration tests for enterprise tools with JSON themes parameter.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastmcp import Context
from qdrant_client import models

from mcp_server_qdrant.mcp_server import QdrantMCPServer
from mcp_server_qdrant.settings import QdrantSettings, EmbeddingProviderSettings
from mcp_server_qdrant.enterprise_config import ENTERPRISE_FILTERABLE_FIELDS
from mcp_server_qdrant.qdrant import Entry


class TestEnterpriseIntegration:
    """Test enterprise tools with JSON themes parameter."""

    @pytest.fixture
    def sample_entries(self):
        """Create sample entries for testing."""
        entry1 = Entry(
            content="export async function loginUser(credentials: LoginCredentials): Promise<AuthResult> {...}",
            metadata={
                "file_path": "src/auth/login.ts",
                "programming_language": "typescript",
                "themes": ["authentication", "security", "api"],
                "complexity_score": 8,
                "repository_id": "taika-st/dtna-chat",
                "file_type": "ts",
                "directory": "src/auth",
                "has_code_patterns": True
            }
        )

        entry2 = Entry(
            content="class DatabaseConnection { async connect(config: DBConfig) {...} }",
            metadata={
                "file_path": "src/db/connection.ts",
                "programming_language": "typescript",
                "themes": ["database", "backend"],
                "complexity_score": 5,
                "repository_id": "taika-st/dtna-chat",
                "file_type": "ts",
                "directory": "src/db",
                "has_code_patterns": True
            }
        )

        entry3 = Entry(
            content="function handleError(error: Error): ErrorResponse {...}",
            metadata={
                "file_path": "src/utils/error-handler.ts",
                "programming_language": "typescript",
                "themes": ["error_handling", "utilities"],
                "complexity_score": 3,
                "repository_id": "taika-st/dtna-chat",
                "file_type": "ts",
                "directory": "src/utils",
                "has_code_patterns": False
            }
        )

        return [entry1, entry2, entry3]

    @pytest.fixture
    async def mcp_server_with_tools(self):
        """Create MCP server with enterprise tools registered."""
        # Mock dependencies
        mock_qdrant = AsyncMock()
        mock_embedding = MagicMock()
        mock_embedding.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])

        # Create settings using environment variables
        with patch.dict('os.environ', {
            'COLLECTION_NAME': 'test_collection',
            'SEARCH_LIMIT': '10',
            'ENTERPRISE_MODE': 'true',
            'ALLOW_ARBITRARY_FILTER': 'false'
        }):
            # Create the server
            with patch('mcp_server_qdrant.mcp_server.QdrantConnector') as mock_connector_class:
                with patch('mcp_server_qdrant.mcp_server.create_embedding_provider') as mock_provider:
                    mock_connector_class.return_value = mock_qdrant
                    mock_provider.return_value = mock_embedding

                    server = QdrantMCPServer(
                        qdrant_settings=QdrantSettings(
                            collection_name="test_collection",
                            filterable_fields=ENTERPRISE_FILTERABLE_FIELDS
                        ),
                        embedding_settings=EmbeddingProviderSettings(
                            provider="test",
                            model="test-model"
                        ),
                        tool_settings=None
                    )

                    # Manually set the mocked dependencies
                    server.qdrant_connector = mock_qdrant
                    server.embedding_provider = mock_embedding

                    return server, mock_qdrant

    @pytest.mark.asyncio
    async def test_search_repository_with_themes_json(self, mcp_server_with_tools, sample_entries):
        """Test search repository with themes as JSON string."""
        server, mock_qdrant = mcp_server_with_tools

        # Configure mock to return filtered results
        mock_qdrant.search.return_value = [sample_entries[0]]  # Return auth entry

        # Get the enterprise search tool
        search_tool = None
        for tool in server.app._tools.values():
            if tool.name == "qdrant-search-repository":
                search_tool = tool.fn
                break

        assert search_tool is not None

        # Create context
        ctx = AsyncMock(spec=Context)

        # Call with themes as JSON string
        result = await search_tool(
            ctx=ctx,
            repository_id="taika-st/dtna-chat",
            query="user authentication",
            themes='["authentication", "security"]',
            programming_language="typescript"
        )

        # Verify no errors
        ctx.error.assert_not_called()

        # Verify search was called
        mock_qdrant.search.assert_called_once()

        # Verify filter was built correctly
        call_args = mock_qdrant.search.call_args
        assert call_args.kwargs["query_filter"] is not None

        # Verify results
        assert len(result) > 0
        assert "Found 1 code snippets" in result[0]
        assert "authentication" in str(result)

    @pytest.mark.asyncio
    async def test_search_repository_invalid_themes_json(self, mcp_server_with_tools):
        """Test search repository with invalid themes JSON."""
        server, mock_qdrant = mcp_server_with_tools

        # Get the enterprise search tool
        search_tool = None
        for tool in server.app._tools.values():
            if tool.name == "qdrant-search-repository":
                search_tool = tool.fn
                break

        ctx = AsyncMock(spec=Context)

        # Call with invalid JSON
        result = await search_tool(
            ctx=ctx,
            repository_id="taika-st/dtna-chat",
            query="authentication",
            themes='["authentication", "security"'  # Missing closing bracket
        )

        # Verify error was reported
        ctx.error.assert_called_once()
        assert "Invalid themes format" in ctx.error.call_args[0][0]

        # Verify error result
        assert len(result) == 1
        assert "Error:" in result[0]
        assert "Invalid themes format" in result[0]

    @pytest.mark.asyncio
    async def test_analyze_patterns_with_themes_json(self, mcp_server_with_tools, sample_entries):
        """Test analyze patterns with themes as JSON string."""
        server, mock_qdrant = mcp_server_with_tools

        # Configure mock to return multiple entries
        mock_qdrant.search.return_value = sample_entries

        # Get the analyze tool
        analyze_tool = None
        for tool in server.app._tools.values():
            if tool.name == "qdrant-analyze-patterns":
                analyze_tool = tool.fn
                break

        assert analyze_tool is not None

        ctx = AsyncMock(spec=Context)

        # Call with themes as JSON string
        result = await analyze_tool(
            ctx=ctx,
            repository_id="taika-st/dtna-chat",
            themes='["authentication", "database"]',
            programming_language="typescript"
        )

        # Verify no errors
        ctx.error.assert_not_called()

        # Verify analysis was performed
        assert len(result) > 0
        assert "Repository Pattern Analysis" in str(result)

    @pytest.mark.asyncio
    async def test_find_implementations_with_themes_json(self, mcp_server_with_tools, sample_entries):
        """Test find implementations with themes as JSON string."""
        server, mock_qdrant = mcp_server_with_tools

        # Configure mock
        mock_qdrant.search.return_value = [sample_entries[0], sample_entries[1]]

        # Get the find implementations tool
        find_tool = None
        for tool in server.app._tools.values():
            if tool.name == "qdrant-find-implementations":
                find_tool = tool.fn
                break

        assert find_tool is not None

        ctx = AsyncMock(spec=Context)

        # Call with themes as JSON string
        result = await find_tool(
            ctx=ctx,
            repository_id="taika-st/dtna-chat",
            pattern_query="user authentication flow",
            themes='["authentication", "api"]',
            min_complexity=5
        )

        # Verify no errors
        ctx.error.assert_not_called()

        # Verify results
        assert len(result) > 0
        assert "Found 2 implementations" in result[0]

    @pytest.mark.asyncio
    async def test_complex_themes_json(self, mcp_server_with_tools):
        """Test themes with special characters and edge cases."""
        server, mock_qdrant = mcp_server_with_tools
        mock_qdrant.search.return_value = []

        search_tool = None
        for tool in server.app._tools.values():
            if tool.name == "qdrant-search-repository":
                search_tool = tool.fn
                break

        ctx = AsyncMock(spec=Context)

        # Test with special characters in themes
        test_cases = [
            '["error_handling", "api/v2", "user-auth"]',  # Special chars
            '["database connection", "user authentication"]',  # Spaces
            '[]',  # Empty array
            '["single"]',  # Single theme
        ]

        for themes_json in test_cases:
            mock_qdrant.search.reset_mock()
            ctx.error.reset_mock()

            result = await search_tool(
                ctx=ctx,
                repository_id="taika-st/dtna-chat",
                query="test query",
                themes=themes_json
            )

            # Should not error
            ctx.error.assert_not_called()
            mock_qdrant.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_all_filters_together(self, mcp_server_with_tools):
        """Test using all available filters together."""
        server, mock_qdrant = mcp_server_with_tools
        mock_qdrant.search.return_value = []

        search_tool = None
        for tool in server.app._tools.values():
            if tool.name == "qdrant-search-repository":
                search_tool = tool.fn
                break

        ctx = AsyncMock(spec=Context)

        # Call with all filters
        result = await search_tool(
            ctx=ctx,
            repository_id="taika-st/dtna-chat",
            query="complex database query optimization",
            themes='["database", "performance", "backend"]',
            programming_language="typescript",
            complexity_score=7,
            file_type="ts",
            directory="src/db",
            has_code_patterns=True
        )

        # Verify no errors
        ctx.error.assert_not_called()

        # Verify search was called with all filters
        mock_qdrant.search.assert_called_once()
        call_args = mock_qdrant.search.call_args

        # Verify a filter was constructed
        assert call_args.kwargs["query_filter"] is not None

    @pytest.mark.asyncio
    async def test_themes_not_json_string(self, mcp_server_with_tools):
        """Test error when themes is not a JSON string."""
        server, mock_qdrant = mcp_server_with_tools

        search_tool = None
        for tool in server.app._tools.values():
            if tool.name == "qdrant-search-repository":
                search_tool = tool.fn
                break

        ctx = AsyncMock(spec=Context)

        # Test various invalid inputs
        invalid_themes = [
            "authentication",  # Plain string, not JSON
            "['auth']",  # Single quotes
            "{themes: ['auth']}",  # Object instead of array
            "null",  # JSON null
            "true",  # Boolean
            "123",  # Number
        ]

        for invalid_theme in invalid_themes:
            ctx.error.reset_mock()

            result = await search_tool(
                ctx=ctx,
                repository_id="taika-st/dtna-chat",
                query="test",
                themes=invalid_theme
            )

            # Should report error
            ctx.error.assert_called_once()
            assert len(result) == 1
            assert "Error:" in result[0]
