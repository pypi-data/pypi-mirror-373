import pytest
from unittest.mock import AsyncMock, Mock, patch
from typing import List, Dict, Any

from mcp_server_qdrant.enterprise_tools import (
    search_repository,
    analyze_repository_patterns,
    find_implementations,
    format_code_entry,
    _analyze_code_patterns,
    _extract_implementation_context
)
from mcp_server_qdrant.qdrant import Entry, QdrantConnector
from mcp_server_qdrant.settings import QdrantSettings, ToolSettings
from mcp_server_qdrant.enterprise_config import get_enterprise_filterable_fields_with_conditions


class TestEnterpriseTools:
    """Test suite for enterprise GitHub codebase search tools."""

    @pytest.fixture
    def sample_metadata(self):
        """Sample metadata matching GitHub codebase structure."""
        return {
            "source": "https://github.com/taika-st/dtna-chat/blob/main/src/lib/auth/login.ts",
            "file_path": "src/lib/auth/login.ts",
            "file_name": "login.ts",
            "file_type": "ts",
            "repository": "taika-st/dtna-chat",
            "branch": "main",
            "sha": "abc123def456",
            "size": 1245,
            "directory": "src/lib/auth",
            "start_index": 0,
            "content_type": "code",
            "programming_language": "typescript",
            "chunk_length": 423,
            "line_count": 18,
            "word_count": 87,
            "has_code_patterns": True,
            "has_comments": True,
            "complexity_score": 7,
            "themes": ["authentication", "frontend", "api"],
            "repository_id": "taika-st/dtna-chat",
            "indexed_at": "2025-01-01T12:00:00Z",
            "document_id": "test-doc-123"
        }

    @pytest.fixture
    def sample_entry(self, sample_metadata):
        """Sample Entry with realistic code content."""
        return Entry(
            content="""export async function loginUser(credentials: LoginCredentials): Promise<AuthResult> {
  try {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials)
    });

    if (!response.ok) {
      throw new Error('Authentication failed');
    }

    const authData = await response.json();
    return { success: true, token: authData.token };
  } catch (error) {
    return { success: false, error: error.message };
  }
}""",
            metadata=sample_metadata
        )

    @pytest.fixture
    def mock_qdrant_connector(self):
        """Mock QdrantConnector for testing."""
        connector = AsyncMock(spec=QdrantConnector)
        return connector

    @pytest.fixture
    def mock_context(self):
        """Mock FastMCP Context."""
        context = AsyncMock()
        context.debug = AsyncMock()
        return context

    @pytest.fixture
    def filterable_fields(self):
        """Get enterprise filterable fields configuration."""
        return get_enterprise_filterable_fields_with_conditions()

    def test_format_code_entry_with_metadata(self, sample_entry):
        """Test code entry formatting with full metadata."""
        result = format_code_entry(sample_entry, "taika-st/dtna-chat")

        assert "<code_snippet>" in result
        assert "<repository>taika-st/dtna-chat</repository>" in result
        assert "<file_path>src/lib/auth/login.ts</file_path>" in result
        assert "<programming_language>typescript</programming_language>" in result
        assert "<themes>authentication, frontend, api</themes>" in result
        assert "<complexity_score>7</complexity_score>" in result
        assert "loginUser" in result  # Content should be included

    def test_format_code_entry_without_metadata(self):
        """Test code entry formatting without metadata."""
        entry = Entry(content="console.log('hello');", metadata=None)
        result = format_code_entry(entry, "test/repo")

        assert "<code_snippet>" in result
        assert "<repository>test/repo</repository>" in result
        assert "console.log('hello');" in result
        assert "Unknown file" not in result  # Should handle gracefully

    @pytest.mark.asyncio
    async def test_search_repository_basic(self, mock_context, mock_qdrant_connector,
                                          sample_entry, filterable_fields):
        """Test basic repository search functionality."""
        # Setup
        mock_qdrant_connector.search.return_value = [sample_entry]

        # Execute
        result = await search_repository(
            mock_context,
            mock_qdrant_connector,
            search_limit=10,
            filterable_fields_with_conditions=filterable_fields,
            repository_id="taika-st/dtna-chat",
            query="authentication login",
            collection_name="test_collection"
        )

        # Verify
        assert len(result) > 0
        assert "Found 1 code snippets" in result[0]
        assert "taika-st/dtna-chat" in result[0]
        mock_qdrant_connector.search.assert_called_once()

        # Verify search was called with correct parameters
        call_args = mock_qdrant_connector.search.call_args
        assert call_args[0][0] == "authentication login"  # query
        assert call_args.kwargs["collection_name"] == "test_collection"
        assert call_args.kwargs["limit"] == 10

    @pytest.mark.asyncio
    async def test_search_repository_with_filters(self, mock_context, mock_qdrant_connector,
                                                 sample_entry, filterable_fields):
        """Test repository search with additional filters."""
        mock_qdrant_connector.search.return_value = [sample_entry]

        result = await search_repository(
            mock_context,
            mock_qdrant_connector,
            search_limit=10,
            filterable_fields_with_conditions=filterable_fields,
            repository_id="taika-st/dtna-chat",
            query="database query",
            collection_name="test_collection"
        )

        assert len(result) > 0
        mock_context.debug.assert_called()

        # Check that debug was called with filter information
        debug_calls = [call.args[0] for call in mock_context.debug.call_args_list]
        filter_debug_call = next((call for call in debug_calls if "Applied filters" in call), None)
        assert filter_debug_call is not None
        assert "repository_id" in filter_debug_call

    @pytest.mark.asyncio
    async def test_search_repository_no_results(self, mock_context, mock_qdrant_connector,
                                               filterable_fields):
        """Test repository search with no results."""
        mock_qdrant_connector.search.return_value = []

        result = await search_repository(
            mock_context,
            mock_qdrant_connector,
            search_limit=10,
            filterable_fields_with_conditions=filterable_fields,
            repository_id="taika-st/dtna-chat",
            query="nonexistent pattern",
            collection_name="test_collection"
        )

        assert len(result) == 1
        assert "No results found" in result[0]
        assert "taika-st/dtna-chat" in result[0]

    @pytest.mark.asyncio
    async def test_analyze_repository_patterns(self, mock_context, mock_qdrant_connector,
                                              sample_entry, filterable_fields):
        """Test repository pattern analysis."""
        # Create multiple entries for better analysis
        entries = [sample_entry]
        for i in range(3):
            metadata = sample_entry.metadata.copy()
            metadata.update({
                "file_path": f"src/lib/component{i}.ts",
                "programming_language": "typescript" if i < 2 else "javascript",
                "themes": ["frontend", "ui"] if i == 0 else ["database", "backend"],
                "complexity_score": i + 3
            })
            entries.append(Entry(content=f"// Component {i}", metadata=metadata))

        mock_qdrant_connector.search.return_value = entries

        result = await analyze_repository_patterns(
            mock_context,
            mock_qdrant_connector,
            search_limit=10,
            filterable_fields_with_conditions=filterable_fields,
            repository_id="taika-st/dtna-chat",
            collection_name="test_collection"
        )

        assert len(result) > 0
        analysis_text = " ".join(result)
        assert "Repository Pattern Analysis" in analysis_text
        assert "Programming Languages" in analysis_text
        assert "Code Themes" in analysis_text
        assert "typescript" in analysis_text.lower()

    @pytest.mark.asyncio
    async def test_analyze_repository_patterns_with_filters(self, mock_context, mock_qdrant_connector,
                                                           sample_entry, filterable_fields):
        """Test repository analysis with specific filters."""
        mock_qdrant_connector.search.return_value = [sample_entry]

        result = await analyze_repository_patterns(
            mock_context,
            mock_qdrant_connector,
            search_limit=10,
            filterable_fields_with_conditions=filterable_fields,
            repository_id="taika-st/dtna-chat",
            collection_name="test_collection",
            themes=["authentication"],
            programming_language="typescript",
            directory="src/lib/auth"
        )

        assert len(result) > 0
        mock_context.debug.assert_called()

        # Verify filters were applied
        debug_calls = [call.args[0] for call in mock_context.debug.call_args_list]
        filter_debug_call = next((call for call in debug_calls if "Analysis filters" in call), None)
        assert filter_debug_call is not None

    @pytest.mark.asyncio
    async def test_find_implementations(self, mock_context, mock_qdrant_connector,
                                       sample_entry, filterable_fields):
        """Test finding implementations functionality."""
        mock_qdrant_connector.search.return_value = [sample_entry]

        result = await find_implementations(
            mock_context,
            mock_qdrant_connector,
            search_limit=5,
            filterable_fields_with_conditions=filterable_fields,
            repository_id="taika-st/dtna-chat",
            pattern_query="user authentication",
            collection_name="test_collection",
            themes=["authentication"],
            programming_language="typescript"
        )

        assert len(result) > 0
        assert "Found 1 implementations" in result[0]
        assert "user authentication" in result[0]
        assert "<implementation rank=\"1\">" in result[1]

        # Verify search was called with the pattern query
        mock_qdrant_connector.search.assert_called_once()
        call_args = mock_qdrant_connector.search.call_args
        assert call_args[0][0] == "user authentication"

    @pytest.mark.asyncio
    async def test_find_implementations_no_results(self, mock_context, mock_qdrant_connector,
                                                  filterable_fields):
        """Test find implementations with no results."""
        mock_qdrant_connector.search.return_value = []

        result = await find_implementations(
            mock_context,
            mock_qdrant_connector,
            search_limit=5,
            filterable_fields_with_conditions=filterable_fields,
            repository_id="taika-st/dtna-chat",
            pattern_query="nonexistent pattern",
            collection_name="test_collection"
        )

        assert len(result) == 1
        assert "No implementations found" in result[0]
        assert "nonexistent pattern" in result[0]

    def test_analyze_code_patterns_multiple_entries(self, sample_entry):
        """Test code pattern analysis with multiple diverse entries."""
        # Create diverse entries for analysis
        entries = []

        # TypeScript auth file
        entries.append(sample_entry)

        # Python database file
        py_metadata = sample_entry.metadata.copy()
        py_metadata.update({
            "file_path": "backend/db/models.py",
            "programming_language": "python",
            "file_type": "py",
            "themes": ["database", "backend", "models"],
            "complexity_score": 5,
            "directory": "backend/db"
        })
        entries.append(Entry(content="class User(BaseModel):", metadata=py_metadata))

        # JavaScript frontend file
        js_metadata = sample_entry.metadata.copy()
        js_metadata.update({
            "file_path": "components/Button.jsx",
            "programming_language": "javascript",
            "file_type": "jsx",
            "themes": ["frontend", "ui", "components"],
            "complexity_score": 3,
            "directory": "components"
        })
        entries.append(Entry(content="export const Button = () => {", metadata=js_metadata))

        result = _analyze_code_patterns(entries, "test/repo")

        analysis_text = " ".join(result)
        assert "Repository Pattern Analysis: test/repo" in analysis_text
        assert "typescript" in analysis_text.lower()
        assert "python" in analysis_text.lower()
        assert "javascript" in analysis_text.lower()
        assert "authentication" in analysis_text.lower()
        assert "database" in analysis_text.lower()
        assert "Average complexity score" in analysis_text

    def test_analyze_code_patterns_empty(self):
        """Test code pattern analysis with no entries."""
        result = _analyze_code_patterns([], "empty/repo")

        assert len(result) == 1
        assert "No code entries available" in result[0]
        assert "empty/repo" in result[0]

    def test_extract_implementation_context(self, sample_entry):
        """Test implementation context extraction."""
        result = _extract_implementation_context(sample_entry)

        assert "<context>" in result
        assert "<location>src/lib/auth/login.ts</location>" in result
        assert "<themes>authentication, frontend, api</themes>" in result
        assert "<complexity>7</complexity>" in result
        assert "<lines>18</lines>" in result
        assert "<structured_patterns>Yes</structured_patterns>" in result

    def test_extract_implementation_context_no_metadata(self):
        """Test implementation context extraction without metadata."""
        entry = Entry(content="test code", metadata=None)
        result = _extract_implementation_context(entry)

        assert "<context>" in result
        assert "No metadata available" in result

    @pytest.mark.asyncio
    async def test_enterprise_tools_integration(self, monkeypatch):
        """Test enterprise tools integration with MCP server."""
        # Set enterprise mode
        monkeypatch.setenv("COLLECTION_NAME", "test")

        qdrant_settings = QdrantSettings()
        tool_settings = ToolSettings()

        # Test that settings load correctly
        assert qdrant_settings.collection_name == "test"

        # Verify enterprise filterable fields are available
        fields = qdrant_settings.filterable_fields_dict()
        assert "repository_id" in fields
        assert "themes" in fields
        assert fields["repository_id"].required is True

    @pytest.mark.parametrize("repository_id,query,expected_in_output", [
        ("owner/repo", "authentication", "owner/repo"),
        ("test-org/my-app", "database query", "test-org/my-app"),
        ("user/project", "api endpoints", "api endpoints"),
    ])
    @pytest.mark.asyncio
    async def test_search_repository_parameterized(self, mock_context, mock_qdrant_connector,
                                                  sample_entry, filterable_fields,
                                                  repository_id, query, expected_in_output):
        """Test repository search with various parameters."""
        mock_qdrant_connector.search.return_value = [sample_entry]

        result = await search_repository(
            mock_context,
            mock_qdrant_connector,
            search_limit=10,
            filterable_fields_with_conditions=filterable_fields,
            repository_id=repository_id,
            query=query,
            collection_name="test_collection"
        )

        result_text = " ".join(result)
        assert expected_in_output in result_text

    def test_filterable_fields_compatibility(self, filterable_fields):
        """Test that enterprise filterable fields are properly configured."""
        # Required fields
        assert "repository_id" in filterable_fields
        assert filterable_fields["repository_id"].required is True

        # Theme field with array support
        assert "themes" in filterable_fields
        assert filterable_fields["themes"].condition == "any"

        # Common refinement fields
        expected_fields = [
            "programming_language", "file_type", "directory", "complexity_score",
            "has_code_patterns", "has_comments", "size", "line_count"
        ]
        for field in expected_fields:
            assert field in filterable_fields, f"Missing field: {field}"

    @pytest.mark.asyncio
    async def test_error_handling_in_search(self, mock_context, mock_qdrant_connector,
                                           filterable_fields):
        """Test error handling in search operations."""
        # Setup mock to raise an exception
        mock_qdrant_connector.search.side_effect = Exception("Connection error")

        with pytest.raises(Exception) as exc_info:
            await search_repository(
                mock_context,
                mock_qdrant_connector,
                search_limit=10,
                filterable_fields_with_conditions=filterable_fields,
                repository_id="test/repo",
                query="test query",
                collection_name="test_collection"
            )

        assert "Connection error" in str(exc_info.value)

    def test_themes_array_handling(self, sample_metadata):
        """Test that themes arrays are properly handled in formatting."""
        # Test with themes array
        entry_with_themes = Entry(
            content="test code",
            metadata={**sample_metadata, "themes": ["auth", "api", "frontend"]}
        )

        result = format_code_entry(entry_with_themes, "test/repo")
        assert "<themes>auth, api, frontend</themes>" in result

        # Test with empty themes
        entry_empty_themes = Entry(
            content="test code",
            metadata={**sample_metadata, "themes": []}
        )

        result_empty = format_code_entry(entry_empty_themes, "test/repo")
        assert "<themes>None</themes>" in result_empty
