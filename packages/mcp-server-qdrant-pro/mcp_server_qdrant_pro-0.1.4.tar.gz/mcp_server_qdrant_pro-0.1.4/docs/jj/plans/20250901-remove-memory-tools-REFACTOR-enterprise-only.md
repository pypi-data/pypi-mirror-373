# Working Set Plan

**JJ Change ID**: zysnlpsw
**JJ Message**: REFACTOR: Remove memory tools and focus on enterprise-only functionality
**Date Created**: 2025-09-01
**Author**: Assistant

## Objective
Remove all memory-related tools from the MCP server and focus exclusively on enterprise GitHub codebase search functionality. Simplify the codebase by eliminating conditional enterprise mode and making enterprise tools the default (and only) behavior.

## Requirements
- [ ] Remove all memory tools (qdrant-store, qdrant-find, etc.)
- [ ] Remove enterprise_mode conditional logic
- [ ] Simplify tool registration to always use enterprise tools
- [ ] Update tool names to remove "qdrant-" prefix for cleaner API
- [ ] Fix all tests to match new structure
- [ ] Clean up unused imports and settings
- [ ] Update documentation and descriptions
- [ ] Ensure backward compatibility is clearly documented

## Technology Stack Decision
### Evaluated Options
1. **Option A**: Keep memory tools as optional features
   - Pros:
     - Backward compatibility maintained
     - More flexible for different use cases
   - Cons:
     - Code complexity with conditional logic
     - Maintenance burden for unused features
     - Confusing API with mixed purposes

2. **Option B**: Remove memory tools entirely, enterprise-only
   - Pros:
     - Simplified codebase focused on single purpose
     - Cleaner API without conditional behavior
     - Easier to maintain and test
     - Clear value proposition as GitHub code search tool
   - Cons:
     - Breaking change for existing memory tool users
     - Need to update all documentation

### Selected Approach
**Option B** - Enterprise-only focus. The server's primary value is in GitHub codebase search, and the memory tools were generic and less differentiated. This creates a more focused, maintainable product.

## Implementation Milestones
1. **Milestone 1**: Complete memory tool removal and fix broken references - Test checkpoint
2. **Milestone 2**: Update all tests to match new structure and tool names - Test checkpoint
3. **Milestone 3**: Clean up settings, imports, and documentation - Test checkpoint
4. **Milestone 4**: Validate end-to-end functionality and update README - Test checkpoint

## Current State Analysis
### What User Has Done ✅
- Removed memory tools from mcp_server.py setup_tools() method
- Simplified tool registration to enterprise tools only
- Changed tool names from "qdrant-search-repository" to "search-repository"
- Removed enterprise_mode conditional logic from tool setup

### What Needs Completion ❌
- Tests still expect old tool names and enterprise_mode setting
- Settings classes still contain memory tool references
- Unused imports need cleanup (wrap_filters, Annotated, Field, etc.)
- Tool descriptions in ToolSettings reference memory functionality
- enterprise_config.py may have unused enterprise mode logic
- Documentation needs updating for new API

## Detailed Changes Required

### 1. Settings Cleanup
- Remove enterprise_mode from QdrantSettings
- Update ToolSettings descriptions to remove memory tool references
- Remove unused filterable field logic if no longer needed
- Simplify settings validation

### 2. Test Fixes
- Update test_enterprise_tools.py to use new tool names
- Remove enterprise_mode expectations from tests
- Fix search_repository parameter expectations
- Update integration tests for new API structure

### 3. Code Cleanup
- Remove unused imports from mcp_server.py
- Clean up enterprise_config.py if enterprise mode logic is unused
- Update main.py and server.py if needed
- Remove memory tool related utilities

### 4. Documentation Updates
- Update README.md with new tool names and enterprise-only focus
- Update docstrings to reflect new API
- Create migration guide for users upgrading from memory tools
- Update examples and usage instructions

## Breaking Changes Documentation
### Tool Name Changes
- `qdrant-search-repository` → `search-repository`
- `qdrant-analyze-patterns` → `analyze-repository-patterns`
- `qdrant-find-implementations` → `find-repository-implementations`

### Removed Tools
- `qdrant-store` (memory storage)
- `qdrant-find` (memory search)
- Any other memory-related tools

### Removed Settings
- `enterprise_mode` setting (always enabled now)
- Memory tool specific settings

## Success Criteria
- [ ] All tests pass with new tool names and structure
- [ ] No unused imports or dead code remains
- [ ] Tool registration works correctly without conditional logic
- [ ] Enterprise functionality works as expected
- [ ] Clear documentation for breaking changes
- [ ] Migration guide available for existing users
- [ ] README reflects new enterprise-only focus

## Rollback Instructions
If this refactoring causes issues:
1. Restore memory tool functions from previous commit
2. Add back enterprise_mode conditional logic
3. Restore original tool names with "qdrant-" prefix
4. Revert settings changes
5. Use `jj restore --from <previous-commit>` for full rollback
