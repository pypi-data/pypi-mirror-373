# Working Set Plan

**JJ Change ID**: dcb3299ff
**JJ Message**: FEAT: extend existing logic and expose deep meta search tools
**Date Created**: 2025-09-01
**Author**: Assistant

## Objective
Transform the existing MCP server from a personal knowledge management system into an enterprise-grade tool for semantic search of vectorized GitHub codebases. The new system will provide extensive search, retrieve, and processing capabilities based on rich metadata, enabling queries like "tell me how authentication is implemented in repository taika-st/dtna-chat."

## Requirements
- [ ] Replace personal memory-focused tools with enterprise code search tools
- [ ] Implement repository-first filtering (filter by repository_id as primary constraint)
- [ ] Support complex metadata-based search queries across multiple dimensions
- [ ] Provide tools for code pattern analysis across repositories
- [ ] Maintain backward compatibility where possible
- [ ] Support rich metadata fields (file_path, file_type, programming_language, themes, etc.)
- [ ] Implement hierarchical filtering (repository -> directory -> file type -> themes)
- [ ] Add code-specific search capabilities (complexity_score, has_code_patterns, etc.)
- [ ] Determine optimal deployment strategy for Python MCP servers

## Technology Stack Decision
### Evaluated Options
1. **Extend Current Architecture**: 
   - Pros: Leverage existing FastMCP framework, minimal breaking changes, proven Qdrant integration
   - Cons: May carry forward some personal-use assumptions, need careful refactoring

2. **Complete Rewrite**: 
   - Pros: Clean slate, purpose-built for enterprise use, no legacy constraints
   - Cons: High risk, more time, lose existing proven patterns

3. **Hybrid Approach**: 
   - Pros: Keep proven core (Qdrant connector, embedding), replace tools layer
   - Cons: More complex migration, potential inconsistencies

### Selected Approach
**Hybrid Approach** - Retain proven core infrastructure (Qdrant connector, embedding providers, FastMCP framework) while completely redesigning the tools layer for enterprise code search. This balances risk with functionality while allowing us to leverage existing robust components.

## Implementation Milestones
1. **Milestone 1**: Analyze current metadata structure and design new filterable fields configuration for code search - Test checkpoint
2. **Milestone 2**: Implement new enterprise tools (repository search, code pattern search, metadata analysis) - Test checkpoint  
3. **Milestone 3**: Update configuration system and deployment strategy, validate end-to-end functionality - Test checkpoint

## Success Criteria
- Can execute repository-scoped queries like "show authentication patterns in taika-st/dtna-chat"
- Supports hierarchical filtering across all metadata dimensions
- Maintains fast search performance with complex filters
- Clear deployment path for enterprise users (uvx compatibility)
- Comprehensive documentation for new enterprise features
- Backward compatibility for basic search functionality