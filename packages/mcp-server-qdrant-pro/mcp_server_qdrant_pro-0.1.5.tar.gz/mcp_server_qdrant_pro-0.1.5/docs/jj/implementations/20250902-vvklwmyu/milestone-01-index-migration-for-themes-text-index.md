# Milestone 01: Ensure TEXT index for themes on existing collections

**JJ Change ID**: vvklwmyu
**Parent Message**: FIX: analyze-pattern tool returns any value in themes field as index required but not found
**Implementation Date**: 2025-09-02 15:04
**Status**: ✅ Success

## What Was Attempted
Implement an idempotent index migration so Qdrant payload indexes (including TEXT for `metadata.themes`) are created even when the collection already exists. This removes the 400 error raised by `qdrant-analyze-patterns` when `themes` is provided.

## Files Modified
- `src/mcp_server_qdrant/qdrant.py` 
  - `_ensure_collection_exists`: now always attempts to create configured payload indexes and gracefully ignores already-exists errors.
  - `search()`: calls `_ensure_collection_exists()` before querying to ensure indexes are present at query time.

## Discoveries & Deviations
### Documentation Issues
- None observed.

### Scope Adjustments
- Added proactive index-ensuring step in `search()` to guarantee indexes are present for all tools, not only on collection creation.

### Technical Decisions
#### Why This Approach
- Keeps behavior idempotent and safe for existing collections without requiring manual migration.
- Centralizes index enforcement in one place before query execution.

#### What Didn't Work
- Relying solely on collection-creation time index setup fails for collections created prior to the full-text themes change.

## Testing Results
```bash
# Commands run
uv run pytest -q
```
- Test output: 80 passed
- Issues found: None

## Next Steps
- [ ] Validate via MCP Inspector: call `qdrant-analyze-patterns` with `themes` populated and confirm no 400 errors.
- [ ] Consider a brief note in `README.md` about automatic index creation for existing collections and the read-only caveat.
- [ ] If `QDRANT_READ_ONLY=true` in prod, schedule a maintenance window to allow index creation once, or pre-create indexes.

## Rollback Instructions
- Revert changes in `src/mcp_server_qdrant/qdrant.py` restoring previous behavior where payload indexes are only created on collection creation and not ensured during search.
