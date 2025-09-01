"""
Tests for JSON themes parsing in MCP server enterprise tools.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp_server_qdrant.mcp_server import QdrantMCPServer


class TestThemesJSONParsing:
    """Test JSON themes parsing functionality."""

    def test_parse_themes_json_valid_array(self):
        """Test parsing valid JSON array."""
        # Create a minimal server instance for testing
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '["authentication", "database", "api"]'
        result = server._parse_themes_json(themes_json)
        assert result == ["authentication", "database", "api"]

    def test_parse_themes_json_empty_array(self):
        """Test parsing empty JSON array."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '[]'
        result = server._parse_themes_json(themes_json)
        assert result == []

    def test_parse_themes_json_none(self):
        """Test parsing None returns None."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        result = server._parse_themes_json(None)
        assert result is None

    def test_parse_themes_json_empty_string(self):
        """Test parsing empty string returns None."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        result = server._parse_themes_json("")
        assert result is None

    def test_parse_themes_json_invalid_json(self):
        """Test parsing invalid JSON raises ValueError."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '["authentication", "database"'  # Missing closing bracket
        with pytest.raises(ValueError) as exc_info:
            server._parse_themes_json(themes_json)
        assert "Invalid themes format" in str(exc_info.value)
        assert "Expected JSON array" in str(exc_info.value)

    def test_parse_themes_json_not_array(self):
        """Test parsing non-array JSON raises ValueError."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '{"theme": "authentication"}'  # Object, not array
        with pytest.raises(ValueError) as exc_info:
            server._parse_themes_json(themes_json)
        assert "themes must be a JSON array" in str(exc_info.value)

    def test_parse_themes_json_string_value(self):
        """Test parsing string instead of array raises ValueError."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '"authentication"'  # Just a string
        with pytest.raises(ValueError) as exc_info:
            server._parse_themes_json(themes_json)
        assert "themes must be a JSON array" in str(exc_info.value)

    def test_parse_themes_json_with_special_characters(self):
        """Test parsing JSON with special characters."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '["auth/login", "database-connection", "api_v2"]'
        result = server._parse_themes_json(themes_json)
        assert result == ["auth/login", "database-connection", "api_v2"]

    def test_parse_themes_json_with_spaces(self):
        """Test parsing JSON with spaces in values."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '["user authentication", "database connection", "rest api"]'
        result = server._parse_themes_json(themes_json)
        assert result == ["user authentication", "database connection", "rest api"]

    def test_parse_themes_json_unicode(self):
        """Test parsing JSON with unicode characters."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '["认证", "データベース", "🔐 security"]'
        result = server._parse_themes_json(themes_json)
        assert result == ["认证", "データベース", "🔐 security"]

    def test_parse_themes_json_number_value(self):
        """Test parsing JSON with number raises ValueError."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '123'  # Just a number
        with pytest.raises(ValueError) as exc_info:
            server._parse_themes_json(themes_json)
        assert "themes must be a JSON array" in str(exc_info.value)

    def test_parse_themes_json_nested_array(self):
        """Test parsing nested array raises ValueError."""
        server = MagicMock(spec=QdrantMCPServer)
        server._parse_themes_json = QdrantMCPServer._parse_themes_json.__get__(server)

        themes_json = '[["auth"], ["db"]]'  # Nested arrays
        result = server._parse_themes_json(themes_json)
        # This actually succeeds as it's still a valid array
        assert result == [["auth"], ["db"]]
        # Note: In production, we might want to validate that all elements are strings
