# Working Set Plan

**JJ Change ID**: fix-themes
**JJ Message**: FIX: Add themes parameter to enterprise search and handle JSON string input
**Date Created**: 2025-09-01
**Author**: Assistant

## Objective
Fix the inconsistency where the enterprise search tool description mentions using themes but the actual function doesn't accept a themes parameter. Additionally, handle themes as a JSON string for API consistency with other string parameters.

## Requirements
- [ ] Add themes parameter to enterprise_search_repository function
- [ ] Accept themes as JSON string (e.g., '["error_handling", "networking"]')
- [ ] Parse JSON string to list internally before filter processing
- [ ] Add other missing filter parameters mentioned in tool description
- [ ] Maintain backward compatibility with existing integrations
- [ ] Update tests to cover JSON string parsing
- [ ] Ensure consistent API design across all parameters

## Technology Stack Decision
### Evaluated Options
1. **Option A**: Add themes as list[str] parameter and require LLMs to pass arrays
   - Pros: 
     - Type-safe at function level
     - No JSON parsing needed
   - Cons:
     - Inconsistent with other string parameters
     - Difficult for LLMs to handle mixed types
     - Breaks API consistency principle

2. **Option B**: Accept themes as JSON string and parse internally
   - Pros:
     - Consistent API - all parameters are strings
     - Easy for LLMs to use
     - Follows principle of least surprise
   - Cons:
     - Requires JSON parsing and validation
     - Need to handle parsing errors gracefully

### Selected Approach
**Option B** - Accept themes as JSON string. This provides the best user experience and maintains API consistency. All parameters will be strings, making it straightforward for LLMs and other clients.

## Implementation Milestones
1. **Milestone 1**: Add themes parameter to enterprise_search_repository with JSON parsing - Test checkpoint
2. **Milestone 2**: Add other filter parameters (programming_language, etc.) with consistent string handling - Test checkpoint
3. **Milestone 3**: Update tests and validate backward compatibility - Test checkpoint

## Success Criteria
- [ ] Enterprise search accepts themes as JSON string: '["authentication", "database"]'
- [ ] Invalid JSON strings return helpful error messages
- [ ] All filter parameters work as described in tool documentation
- [ ] Existing integrations continue working without changes
- [ ] Tests pass with >90% coverage of new code paths
- [ ] LLMs can successfully use the tool with string parameters