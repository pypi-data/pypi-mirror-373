# Working Set Plan

**JJ Change ID**: zmsstzsq
**JJ Message**: FEAT: Add full text search to theme tags for search-repository
**Date Created**: 2025-09-01
**Author**: [Your Name]

## Objective
Enable full-text search on `themes` metadata so the `search-repository` tool can match partial terms (e.g., "auth" → "authentication") and is no longer limited to exact tag matches.

## Requirements
- [ ] Implement full-text matching for `metadata.themes` in repository-scoped searches
- [ ] Maintain backward compatibility with existing `themes` JSON-array parameter
- [ ] Keep repository scoping mandatory and unaffected
- [ ] Do not degrade performance for typical queries (target parity or better)
- [ ] Add/adjust tests to cover partial matching behavior
- [ ] Update tool descriptions/README where needed
- [ ] Provide safe index migration path (no breaking changes for other fields)

## Technology Stack Decision
### Evaluated Options
1. **Option A: Qdrant full-text index on `metadata.themes` + MatchText**
   - Pros:
     - Native full-text; supports partial and tokenized matches
     - Clear intent separated from semantic vector search
     - Retains structured filtering for other fields
   - Cons:
     - Requires schema/index change (TEXT instead of KEYWORD)
     - Needs code path to build MatchText conditions per term

2. **Option B: Fold themes terms into the semantic `query` string**
   - Pros:
     - No index change; simplest change
   - Cons:
     - Loses explicit filtering semantics on `themes`
     - Harder to reason about precise matches; coupling to embedding behavior

3. **Option C: Hybrid: keep KEYWORD filter and fall back to full-text-like contains**
   - Pros:
     - Incremental; preserves existing behavior
   - Cons:
     - "Contains" over arrays is not supported reliably with KEYWORD index
     - Would be ad-hoc and less robust than native text index

### Selected Approach
Proceed with **Option A**:
- Extend filter/index utilities to support a `text` field type that maps to Qdrant `PayloadSchemaType.TEXT` and uses `MatchText` conditions.
- Migrate `themes` to `text` field type in enterprise filter config.
- When `themes` array is provided, build OR-style MatchText conditions for each term.
- Preserve repository_id exact filter and all other filters as-is.

## Implementation Milestones
1. **Schema & Filter Support** - Test checkpoint
   - Extend `FilterableField.field_type` to include `"text"`
   - Update `make_indexes()` to map `text` → `PayloadSchemaType.TEXT`
   - Update `make_filter()` to support `text` with `MatchText` (accept list or string)

2. **Enterprise Config Update** - Test checkpoint
   - Change `themes` field to `field_type="text"`; update description to note partial matching
   - Keep `condition` as `any` to express OR semantics across provided terms

3. **Tool Integration** - Test checkpoint
   - Ensure `mcp_server.py` parsing of `themes` JSON remains intact
   - Verify generated filters now emit `MatchText` for themes
   - Keep repository scoping mandatory

4. **Tests & Docs** - Test checkpoint
   - Update/add tests (e.g., `tests/test_mcp_server_themes.py`) to assert partial matches
   - Update tool descriptions in `settings.py` and README examples

5. **Performance & Migration** - Test checkpoint
   - Confirm no regressions in search latency for typical limits
   - Document index update impact and rollback steps

## Success Criteria
- `search-repository` returns matches when `themes` terms are provided as partials (e.g., "auth" matches entries tagged with "authentication")
- All existing tests pass; new tests validate partial matching
- No changes required for clients beyond the existing `themes` JSON parameter
- Repository scoping and other filters continue to work as before
