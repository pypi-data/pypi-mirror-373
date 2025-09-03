#!/bin/bash
# Enterprise Mode Environment Variables for mcp-server-qdrant
#
# This file contains example environment variable configurations for running
# mcp-server-qdrant in enterprise mode for GitHub codebase search.
#
# Usage:
#   source examples/enterprise-env-vars.sh
#   uvx mcp-server-qdrant

# =============================================================================
# ENTERPRISE MODE CONFIGURATION
# =============================================================================

# Enable enterprise GitHub codebase search mode
export ENTERPRISE_MODE=true

# =============================================================================
# QDRANT CONNECTION SETTINGS
# =============================================================================

# Qdrant server URL (required)
# Replace with your actual Qdrant cluster URL
export QDRANT_URL="https://your-cluster-id.us-east4-0.gcp.cloud.qdrant.tech:6333"

# Qdrant API key for authentication (required for cloud instances)
# Replace with your actual API key
export QDRANT_API_KEY="your-qdrant-api-key-here"

# Collection name containing vectorized GitHub repositories (required)
# This should point to a collection with GitHub codebase data
export COLLECTION_NAME="github-codebases"

# =============================================================================
# EMBEDDING CONFIGURATION
# =============================================================================

# Embedding model for semantic search (optional)
# Default: sentence-transformers/all-MiniLM-L6-v2
# Other options: sentence-transformers/all-mpnet-base-v2 (higher quality, slower)
export EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Embedding provider (optional)
# Currently only "fastembed" is supported
export EMBEDDING_PROVIDER="fastembed"

# =============================================================================
# SEARCH BEHAVIOR SETTINGS
# =============================================================================

# Maximum number of results returned per search (optional)
# Default: 10, recommended range: 5-20
export QDRANT_SEARCH_LIMIT="15"

# Set to true to disable store operations (recommended for code search)
# This prevents accidental modifications to your codebase collection
export QDRANT_READ_ONLY="true"

# Allow arbitrary filter conditions (optional)
# Default: false (recommended for security)
export QDRANT_ALLOW_ARBITRARY_FILTER="false"

# =============================================================================
# ALTERNATIVE: LOCAL QDRANT SETUP
# =============================================================================

# Uncomment these lines to use a local Qdrant instance instead
# Note: Cannot use both QDRANT_URL and QDRANT_LOCAL_PATH simultaneously
# export QDRANT_LOCAL_PATH="/path/to/local/qdrant/storage"
# unset QDRANT_URL
# unset QDRANT_API_KEY

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

echo "Enterprise mode environment variables set!"
echo ""
echo "Available enterprise tools when running mcp-server-qdrant:"
echo "  - qdrant-search-repository: Search code within a specific repository"
echo "  - qdrant-analyze-patterns: Analyze code patterns and architecture"
echo "  - qdrant-find-implementations: Find implementation examples"
echo ""
echo "Example queries:"
echo "  Repository: 'owner/repo-name'"
echo "  Themes: ['authentication', 'database', 'api', 'frontend']"
echo "  Languages: 'typescript', 'python', 'javascript', 'rust'"
echo ""
echo "Start the server with: uvx mcp-server-qdrant"
echo "Or test locally with: uvx --from . mcp-server-qdrant"
