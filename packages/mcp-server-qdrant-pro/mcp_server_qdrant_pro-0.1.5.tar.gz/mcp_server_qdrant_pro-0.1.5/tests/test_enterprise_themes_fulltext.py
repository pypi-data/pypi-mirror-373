import pytest
from unittest.mock import AsyncMock

from qdrant_client import models

from mcp_server_qdrant.enterprise_config import get_enterprise_filterable_fields_with_conditions
from mcp_server_qdrant.common.filters import make_filter
from mcp_server_qdrant.enterprise_tools import search_repository
from mcp_server_qdrant.qdrant import QdrantConnector, Entry


def test_make_filter_text_themes_produces_should_matchtext():
    fields = get_enterprise_filterable_fields_with_conditions()
    filter_conditions = {
        "repository_id": "owner/repo",
        "themes": ["auth", "db"],
    }

    built = make_filter(fields, filter_conditions)
    # Reconstruct Filter to inspect types
    flt = models.Filter(**built)

    # Ensure repository_id is in must
    assert flt.must is not None

    # Ensure themes are in should as MatchText
    assert flt.should is not None and len(flt.should) >= 2
    for cond in (flt.should if isinstance(flt.should, list) else [flt.should]):
        assert isinstance(cond, models.FieldCondition)
        assert cond.key == "metadata.themes"
        assert isinstance(cond.match, models.MatchText)


@pytest.mark.asyncio
async def test_search_repository_fallback_removes_theme_should(monkeypatch):
    # Prepare a filter that contains a theme-related should condition
    theme_condition = models.FieldCondition(
        key="metadata.themes",
        match=models.MatchText(text="auth"),
    )
    additional = models.Filter(should=[theme_condition])

    # Mock connector: first call returns no results, second returns one
    mock_connector = AsyncMock(spec=QdrantConnector)
    sample_entry = Entry(content="code", metadata={"repository_id": "owner/repo"})

    async def side_effect_search(query, *, collection_name, limit, query_filter):
        # First invocation: no results to trigger fallback
        if not hasattr(side_effect_search, "called"):
            side_effect_search.called = True
            return []
        # Second invocation: ensure theme-related should is removed
        if query_filter and getattr(query_filter, "should", None):
            for cond in (query_filter.should if isinstance(query_filter.should, list) else [query_filter.should]):
                assert not (isinstance(cond, models.FieldCondition) and cond.key == "metadata.themes"), (
                    "Theme-related should should be removed in fallback"
                )
        return [sample_entry]

    mock_connector.search.side_effect = side_effect_search

    # Minimal ctx mock
    class Ctx:
        async def debug(self, *_args, **_kwargs):
            pass

    ctx = Ctx()

    fields = get_enterprise_filterable_fields_with_conditions()

    result = await search_repository(
        ctx,
        mock_connector,
        search_limit=5,
        filterable_fields_with_conditions=fields,
        repository_id="owner/repo",
        query="test",
        collection_name="test_collection",
        query_filter=additional.model_dump(),
    )

    # Should have two calls (initial + fallback)
    assert mock_connector.search.await_count == 2
    assert any("Found" in line for line in result)
