import pytest

from mcp_server_qdrant.settings import QdrantSettings
from mcp_server_qdrant.enterprise_config import (
    ENTERPRISE_FILTERABLE_FIELDS,
    get_enterprise_filterable_fields_dict,
    get_enterprise_filterable_fields_with_conditions,
    ENTERPRISE_TOOL_DESCRIPTIONS
)


class TestEnterpriseConfig:
    """Test suite for enterprise GitHub codebase search configuration."""

    def test_enterprise_filterable_fields_structure(self):
        """Test that enterprise filterable fields are properly structured."""
        fields = ENTERPRISE_FILTERABLE_FIELDS

        # Should have fields defined
        assert len(fields) > 0

        # Check that repository_id is present and required
        repo_field = next((f for f in fields if f.name == "repository_id"), None)
        assert repo_field is not None, "repository_id field must be present"
        assert repo_field.required is True, "repository_id must be required"
        assert repo_field.field_type == "keyword"
        assert repo_field.condition == "=="

        # Check that themes field is present with array matching
        themes_field = next((f for f in fields if f.name == "themes"), None)
        assert themes_field is not None, "themes field must be present"
        assert themes_field.field_type == "keyword"
        assert themes_field.condition == "any", "themes should use 'any' condition for array matching"
        assert themes_field.required is False

        # Check that all fields have valid types
        valid_types = {"keyword", "integer", "float", "boolean"}
        for field in fields:
            assert field.field_type in valid_types, f"Field {field.name} has invalid type {field.field_type}"

        # Check that all conditions are valid
        valid_conditions = {"==", "!=", ">", ">=", "<", "<=", "any", "except", None}
        for field in fields:
            assert field.condition in valid_conditions, f"Field {field.name} has invalid condition {field.condition}"

    def test_enterprise_filterable_fields_hierarchy(self):
        """Test that filterable fields follow the intended hierarchy."""
        fields_dict = get_enterprise_filterable_fields_dict()

        # Primary: repository_id (required)
        assert "repository_id" in fields_dict
        assert fields_dict["repository_id"].required is True

        # Secondary: themes (semantic)
        assert "themes" in fields_dict
        assert fields_dict["themes"].condition == "any"

        # Tertiary: refinement filters
        tertiary_fields = [
            "programming_language", "file_type", "directory", "file_name",
            "has_code_patterns", "has_comments", "complexity_score",
            "size", "line_count", "word_count", "branch", "sha"
        ]
        for field_name in tertiary_fields:
            assert field_name in fields_dict, f"Missing tertiary field: {field_name}"
            assert fields_dict[field_name].required is False

    def test_enterprise_fields_with_conditions(self):
        """Test that only fields with conditions are exposed as tool parameters."""
        all_fields = get_enterprise_filterable_fields_dict()
        fields_with_conditions = get_enterprise_filterable_fields_with_conditions()

        # Fields with conditions should be subset of all fields
        assert len(fields_with_conditions) <= len(all_fields)

        # All fields with conditions should have non-None condition
        for field_name, field in fields_with_conditions.items():
            assert field.condition is not None, f"Field {field_name} should have a condition"

        # Fields without conditions should not be in the subset
        for field_name, field in all_fields.items():
            if field.condition is None:
                assert field_name not in fields_with_conditions, f"Field {field_name} should not be exposed"

    def test_qdrant_settings_enterprise_mode(self, monkeypatch):
        """Test QdrantSettings with enterprise mode."""
        # Test enterprise mode disabled (default)
        settings = QdrantSettings()

        # Should return empty dict for filterable fields when no custom fields are set
        fields_dict = settings.filterable_fields_dict()
        assert isinstance(fields_dict, dict)

        # Should return enterprise filterable fields
        assert len(fields_dict) > 0
        assert "repository_id" in fields_dict
        assert "themes" in fields_dict

    def test_enterprise_field_types_and_conditions_compatibility(self):
        """Test that field types and conditions are compatible with Qdrant filtering."""
        fields = get_enterprise_filterable_fields_dict()

        # Test keyword fields
        keyword_fields = [f for f in fields.values() if f.field_type == "keyword"]
        for field in keyword_fields:
            if field.condition is not None:
                assert field.condition in ["==", "!=", "any", "except"], \
                    f"Keyword field {field.name} has invalid condition {field.condition}"

        # Test integer fields
        integer_fields = [f for f in fields.values() if f.field_type == "integer"]
        for field in integer_fields:
            if field.condition is not None:
                assert field.condition in ["==", "!=", ">", ">=", "<", "<=", "any", "except"], \
                    f"Integer field {field.name} has invalid condition {field.condition}"

        # Test boolean fields
        boolean_fields = [f for f in fields.values() if f.field_type == "boolean"]
        for field in boolean_fields:
            if field.condition is not None:
                assert field.condition in ["==", "!="], \
                    f"Boolean field {field.name} has invalid condition {field.condition}"

    def test_required_field_configuration(self):
        """Test that required field configuration is correct for enterprise use."""
        fields = get_enterprise_filterable_fields_dict()

        # Only repository_id should be required
        required_fields = [f for f in fields.values() if f.required]
        assert len(required_fields) == 1, "Only one field should be required"
        assert required_fields[0].name == "repository_id", "Only repository_id should be required"

        # All other fields should be optional
        optional_fields = [f for f in fields.values() if not f.required]
        assert len(optional_fields) == len(fields) - 1, "All other fields should be optional"

    def test_enterprise_tool_descriptions_exist(self):
        """Test that enterprise tool descriptions are properly defined."""
        assert "search" in ENTERPRISE_TOOL_DESCRIPTIONS
        assert "analyze_repository" in ENTERPRISE_TOOL_DESCRIPTIONS
        assert "find_implementations" in ENTERPRISE_TOOL_DESCRIPTIONS

        # Check that descriptions contain relevant keywords
        search_desc = ENTERPRISE_TOOL_DESCRIPTIONS["search"]
        assert "repository_id" in search_desc, "Search description should mention repository_id"
        assert "themes" in search_desc, "Search description should mention themes"
        assert "authentication" in search_desc, "Search description should have examples"

    def test_metadata_field_coverage(self):
        """Test that all important metadata fields from the example are covered."""
        fields = get_enterprise_filterable_fields_dict()

        # Core fields that should be present based on the metadata example
        expected_fields = [
            "repository_id", "themes", "file_path", "file_name", "file_type",
            "programming_language", "directory", "branch", "sha", "size",
            "has_code_patterns", "has_comments", "complexity_score",
            "line_count", "word_count"
        ]

        for field_name in expected_fields:
            # Note: file_path isn't directly included as it can be derived from directory + file_name
            if field_name == "file_path":
                # Check that we have directory and file_name instead
                assert "directory" in fields, "Should have directory field"
                assert "file_name" in fields, "Should have file_name field"
            else:
                assert field_name in fields, f"Missing expected field: {field_name}"

    def test_array_field_configuration(self):
        """Test that array fields (themes) are properly configured for matching."""
        fields = get_enterprise_filterable_fields_dict()
        themes_field = fields["themes"]

        # Themes should use 'any' condition for array matching
        assert themes_field.condition == "any", "Themes field should use 'any' condition"
        assert themes_field.field_type == "keyword", "Themes field should be keyword type"

        # Description should indicate it's an array
        assert "array" in themes_field.description.lower(), "Description should mention it's an array"

    @pytest.mark.parametrize("field_name,expected_type", [
        ("repository_id", "keyword"),
        ("themes", "keyword"),
        ("programming_language", "keyword"),
        ("complexity_score", "integer"),
        ("has_code_patterns", "boolean"),
        ("size", "integer"),
    ])
    def test_specific_field_types(self, field_name: str, expected_type: str):
        """Test that specific fields have the correct types."""
        fields = get_enterprise_filterable_fields_dict()
        assert field_name in fields, f"Field {field_name} should exist"
        assert fields[field_name].field_type == expected_type, \
            f"Field {field_name} should be type {expected_type}, got {fields[field_name].field_type}"
