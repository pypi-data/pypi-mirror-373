# mcp-server-qdrant: A Qdrant MCP server

[![smithery badge](https://smithery.ai/badge/mcp-server-qdrant)](https://smithery.ai/protocol/mcp-server-qdrant)

> The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that enables
> seamless integration between LLM applications and external data sources and tools. Whether you're building an
> AI-powered IDE, enhancing a chat interface, or creating custom AI workflows, MCP provides a standardized way to
> connect LLMs with the context they need.

This repository is an example of how to create a MCP server for [Qdrant](https://qdrant.tech/), a vector search engine.

## Overview

A Model Context Protocol server for advanced GitHub codebase search using Qdrant vector search engine.
It provides semantic code search capabilities across vectorized GitHub repositories.

### Features
- **Repository-scoped search**: Always filtered by repository for focused results
- **Semantic code search**: Find functionality patterns across codebases
- **Code pattern analysis**: Understand repository structure and common patterns
- **Implementation discovery**: Find examples of specific functionality
- **Rich metadata filtering**: Filter by programming language, themes, complexity, file types, and more
- **Hierarchical filtering**: Repository → themes → refinement filters for optimal search experience



## Components

### Tools

1. `search-repository`
   - Search for code patterns and implementations within a specific GitHub repository
   - Input:
     - `repository_id` (string, required): Repository identifier in format 'owner/repo' (e.g., 'taika-st/dtna-chat')
     - `query` (string): Semantic search query for finding code patterns, functionality, or implementations
     - `themes` (string, optional): JSON array of code themes/patterns to match (e.g., '["authentication", "database"]')
     - `programming_language` (string, optional): Filter by programming language
     - `complexity_score` (integer, optional): Minimum complexity score
     - Additional filterable fields: file_type, directory, has_code_patterns, etc.
   - Returns: Formatted code snippets with rich metadata

2. `analyze-repository-patterns`
   - Analyze code patterns, themes, and architecture within a repository
   - Input:
     - `repository_id` (string, required): Repository identifier
     - `themes` (string, optional): JSON array of specific themes to analyze
     - `programming_language` (string, optional): Focus on specific language
     - `directory` (string, optional): Analyze specific directory
   - Returns: Repository analysis with statistics and insights

3. `find-repository-implementations`
   - Find implementations of specific patterns or functionality within a repository
   - Input:
     - `repository_id` (string, required): Repository identifier
     - `pattern_query` (string): Description of pattern to find (e.g., 'user authentication', 'database connection')
     - `themes` (string, optional): JSON array of expected themes for filtering
     - `programming_language` (string, optional): Expected programming language
     - `min_complexity` (integer, optional): Minimum complexity threshold
   - Returns: Implementations ranked by semantic similarity

## Environment Variables

The configuration of the server is done using environment variables:

| Name                                        | Description                                                         | Default Value                                                     |
|---------------------------------------------|---------------------------------------------------------------------|-------------------------------------------------------------------|
| `QDRANT_URL`                                | URL of the Qdrant server                                            | None                                                              |
| `QDRANT_API_KEY`                            | API key for the Qdrant server                                       | None                                                              |
| `COLLECTION_NAME`                           | Name of the collection containing vectorized GitHub repositories    | None                                                              |
| `QDRANT_LOCAL_PATH`                         | Path to the local Qdrant database (alternative to `QDRANT_URL`)     | None                                                              |
| `QDRANT_SEARCH_LIMIT`                       | Maximum results per search operation                                 | `10`                                                              |
| `QDRANT_ALLOW_ARBITRARY_FILTER`             | Allow arbitrary filter conditions in queries                        | `false`                                                           |
| `EMBEDDING_PROVIDER`                        | Embedding provider to use (currently only "fastembed" is supported) | `fastembed`                                                       |
| `EMBEDDING_MODEL`                           | Name of the embedding model to use                                  | `sentence-transformers/all-MiniLM-L6-v2`                          |
| `TOOL_SEARCH_REPOSITORY_DESCRIPTION`        | Custom description for the search-repository tool                   | See default in [`settings.py`](src/mcp_server_qdrant/settings.py) |
| `TOOL_ANALYZE_PATTERNS_DESCRIPTION`         | Custom description for the analyze-repository-patterns tool         | See default in [`settings.py`](src/mcp_server_qdrant/settings.py) |
| `TOOL_FIND_IMPLEMENTATIONS_DESCRIPTION`     | Custom description for the find-repository-implementations tool     | See default in [`settings.py`](src/mcp_server_qdrant/settings.py) |

### GitHub Codebase Search Configuration

The server is designed for searching vectorized GitHub repositories. Recommended configuration:

| Setting                  | Recommended Value                                                   | Purpose                                   |
|--------------------------|---------------------------------------------------------------------|-------------------------------------------|
| `COLLECTION_NAME`        | `github-codebases` or similar descriptive name                     | Collection with vectorized repositories   |
| `QDRANT_SEARCH_LIMIT`    | `10-50` depending on use case                                       | Balance between relevance and performance |
| `QDRANT_ALLOW_ARBITRARY_FILTER` | `false` (recommended for security)                             | Restrict to predefined filter fields     |

Note: You cannot provide both `QDRANT_URL` and `QDRANT_LOCAL_PATH` at the same time.

> [!IMPORTANT]
> Command-line arguments are not supported anymore! Please use environment variables for all configuration.

### FastMCP Environment Variables

Since `mcp-server-qdrant` is based on FastMCP, it also supports all the FastMCP environment variables. The most
important ones are listed below:

| Environment Variable                  | Description                                               | Default Value |
|---------------------------------------|-----------------------------------------------------------|---------------|
| `FASTMCP_DEBUG`                       | Enable debug mode                                         | `false`       |
| `FASTMCP_LOG_LEVEL`                   | Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO`        |
| `FASTMCP_HOST`                        | Host address to bind the server to                        | `127.0.0.1`   |
| `FASTMCP_PORT`                        | Port to run the server on                                 | `8000`        |
| `FASTMCP_WARN_ON_DUPLICATE_RESOURCES` | Show warnings for duplicate resources                     | `true`        |
| `FASTMCP_WARN_ON_DUPLICATE_TOOLS`     | Show warnings for duplicate tools                         | `true`        |
| `FASTMCP_WARN_ON_DUPLICATE_PROMPTS`   | Show warnings for duplicate prompts                       | `true`        |
| `FASTMCP_DEPENDENCIES`                | List of dependencies to install in the server environment | `[]`          |

## Installation

### Using uvx

When using [`uvx`](https://docs.astral.sh/uv/guides/tools/#running-tools) no specific installation is needed to directly run *mcp-server-qdrant*.

```shell
QDRANT_URL="http://localhost:6333" \
COLLECTION_NAME="my-collection" \
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
uvx mcp-server-qdrant
```

#### Transport Protocols

The server supports different transport protocols that can be specified using the `--transport` flag:

```shell
QDRANT_URL="http://localhost:6333" \
COLLECTION_NAME="my-collection" \
uvx mcp-server-qdrant --transport sse
```

Supported transport protocols:

- `stdio` (default): Standard input/output transport, might only be used by local MCP clients
- `sse`: Server-Sent Events transport, perfect for remote clients
- `streamable-http`: Streamable HTTP transport, perfect for remote clients, more recent than SSE

The default transport is `stdio` if not specified.

When SSE transport is used, the server will listen on the specified port and wait for incoming connections. The default
port is 8000, however it can be changed using the `FASTMCP_PORT` environment variable.

```shell
QDRANT_URL="http://localhost:6333" \
COLLECTION_NAME="my-collection" \
FASTMCP_PORT=1234 \
uvx mcp-server-qdrant --transport sse
```

### Using Docker

A Dockerfile is available for building and running the MCP server:

```bash
# Build the container
docker build -t mcp-server-qdrant .

# Run the container
docker run -p 8000:8000 \
  -e FASTMCP_HOST="0.0.0.0" \
  -e QDRANT_URL="http://your-qdrant-server:6333" \
  -e QDRANT_API_KEY="your-api-key" \
  -e COLLECTION_NAME="your-collection" \
  mcp-server-qdrant
```

> [!TIP]
> Please note that we set `FASTMCP_HOST="0.0.0.0"` to make the server listen on all network interfaces. This is
> necessary when running the server in a Docker container.

### Installing via Smithery

To install Qdrant MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/protocol/mcp-server-qdrant):

```bash
npx @smithery/cli install mcp-server-qdrant --client claude
```

### Manual configuration of Claude Desktop

To use this server with the Claude Desktop app, add the following configuration to the "mcpServers" section of your
`claude_desktop_config.json`:

```json
{
  "qdrant": {
    "command": "uvx",
    "args": ["mcp-server-qdrant"],
    "env": {
      "QDRANT_URL": "https://xyz-example.eu-central.aws.cloud.qdrant.io:6333",
      "QDRANT_API_KEY": "your_api_key",
      "COLLECTION_NAME": "your-collection-name",
      "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
    }
  }
}
```

For local Qdrant mode:

```json
{
  "qdrant": {
    "command": "uvx",
    "args": ["mcp-server-qdrant"],
    "env": {
      "QDRANT_LOCAL_PATH": "/path/to/qdrant/database",
      "COLLECTION_NAME": "your-collection-name",
      "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2"
    }
  }
}
```

This MCP server will automatically create a collection with the specified name if it doesn't exist.

By default, the server will use the `sentence-transformers/all-MiniLM-L6-v2` embedding model to encode memories.
For the time being, only [FastEmbed](https://qdrant.github.io/fastembed/) models are supported.

## Support for other tools

This MCP server can be used with any MCP-compatible client. For example, you can use it with
[Cursor](https://docs.cursor.com/context/model-context-protocol) and [VS Code](https://code.visualstudio.com/docs), which provide built-in support for the Model Context
Protocol.

### Enterprise Mode Examples

#### Personal Memory Mode (Default)
```json
{
  "mcpServers": {
    "qdrant": {
      "command": "uvx",
      "args": ["mcp-server-qdrant"],
      "env": {
        "QDRANT_URL": "https://your-qdrant-cluster.com",
        "QDRANT_API_KEY": "your-api-key",
        "COLLECTION_NAME": "personal-memories"
      }
    }
  }
}
```

#### Enterprise GitHub Codebase Search Mode
```json
{
  "mcpServers": {
    "qdrant-enterprise": {
      "command": "uvx",
      "args": ["mcp-server-qdrant"],
      "env": {
        "ENTERPRISE_MODE": "true",
        "QDRANT_URL": "https://your-qdrant-cluster.com",
        "QDRANT_API_KEY": "your-api-key",
        "COLLECTION_NAME": "github-codebases",
        "QDRANT_READ_ONLY": "true",
        "QDRANT_SEARCH_LIMIT": "10"
      }
    }
  }
}
```

### Using with Cursor/Windsurf

You can configure this MCP server to work as a code search tool for Cursor or Windsurf by customizing the tool
descriptions:

```bash
QDRANT_URL="http://localhost:6333" \
COLLECTION_NAME="code-snippets" \
TOOL_STORE_DESCRIPTION="Store reusable code snippets for later retrieval. \
The 'information' parameter should contain a natural language description of what the code does, \
while the actual code should be included in the 'metadata' parameter as a 'code' property. \
The value of 'metadata' is a Python dictionary with strings as keys. \
Use this whenever you generate some code snippet." \
TOOL_FIND_DESCRIPTION="Search for relevant code snippets based on natural language descriptions. \
The 'query' parameter should describe what you're looking for, \
and the tool will return the most relevant code snippets. \
Use this when you need to find existing code snippets for reuse or reference." \
uvx mcp-server-qdrant --transport sse # Enable SSE transport
```

In Cursor/Windsurf, you can then configure the MCP server in your settings by pointing to this running server using
SSE transport protocol. The description on how to add an MCP server to Cursor can be found in the [Cursor
documentation](https://docs.cursor.com/context/model-context-protocol#adding-an-mcp-server-to-cursor). If you are
running Cursor/Windsurf locally, you can use the following URL:

```
http://localhost:8000/sse
```

> [!TIP]
> We suggest SSE transport as a preferred way to connect Cursor/Windsurf to the MCP server, as it can support remote
> connections. That makes it easy to share the server with your team or use it in a cloud environment.

This configuration transforms the Qdrant MCP server into a specialized code search tool that can:

1. Store code snippets, documentation, and implementation details
2. Retrieve relevant code examples based on semantic search
3. Help developers find specific implementations or usage patterns

You can populate the database by storing natural language descriptions of code snippets (in the `information` parameter)
along with the actual code (in the `metadata.code` property), and then search for them using natural language queries
that describe what you're looking for.

> [!NOTE]
> The tool descriptions provided above are examples and may need to be customized for your specific use case. Consider
> adjusting the descriptions to better match your team's workflow and the specific types of code snippets you want to
> store and retrieve.

**If you have successfully installed the `mcp-server-qdrant`, but still can't get it to work with Cursor, please
consider creating the [Cursor rules](https://docs.cursor.com/context/rules-for-ai) so the MCP tools are always used when
the agent produces a new code snippet.** You can restrict the rules to only work for certain file types, to avoid using
the MCP server for the documentation or other types of content.

### Using with Claude Code

You can enhance Claude Code's capabilities by connecting it to this MCP server, enabling semantic search over your
existing codebase.

#### Setting up mcp-server-qdrant

1. Add the MCP server to Claude Code:

    ```shell
    # Add mcp-server-qdrant configured for code search
    claude mcp add code-search \
    -e QDRANT_URL="http://localhost:6333" \
    -e COLLECTION_NAME="code-repository" \
    -e EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2" \
    -e TOOL_STORE_DESCRIPTION="Store code snippets with descriptions. The 'information' parameter should contain a natural language description of what the code does, while the actual code should be included in the 'metadata' parameter as a 'code' property." \
    -e TOOL_FIND_DESCRIPTION="Search for relevant code snippets using natural language. The 'query' parameter should describe the functionality you're looking for." \
    -- uvx mcp-server-qdrant
    ```

2. Verify the server was added:

    ```shell
    claude mcp list
    ```

#### Using Semantic Code Search in Claude Code

Tool descriptions, specified in `TOOL_STORE_DESCRIPTION` and `TOOL_FIND_DESCRIPTION`, guide Claude Code on how to use
the MCP server. The ones provided above are examples and may need to be customized for your specific use case. However,
Claude Code should be already able to:

1. Use the `qdrant-store` tool to store code snippets with descriptions.
2. Use the `qdrant-find` tool to search for relevant code snippets using natural language.

### Run MCP server in Development Mode

The MCP server can be run in development mode using the `mcp dev` command. This will start the server and open the MCP
inspector in your browser.

```shell
COLLECTION_NAME=mcp-dev fastmcp dev src/mcp_server_qdrant/server.py
```

### Using with VS Code

For one-click installation, click one of the install buttons below:

[![Install with UVX in VS Code](https://img.shields.io/badge/VS_Code-UVX-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=qdrant&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-server-qdrant%22%5D%2C%22env%22%3A%7B%22QDRANT_URL%22%3A%22%24%7Binput%3AqdrantUrl%7D%22%2C%22QDRANT_API_KEY%22%3A%22%24%7Binput%3AqdrantApiKey%7D%22%2C%22COLLECTION_NAME%22%3A%22%24%7Binput%3AcollectionName%7D%22%7D%7D&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantUrl%22%2C%22description%22%3A%22Qdrant+URL%22%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantApiKey%22%2C%22description%22%3A%22Qdrant+API+Key%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22collectionName%22%2C%22description%22%3A%22Collection+Name%22%7D%5D) [![Install with UVX in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-UVX-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=qdrant&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22mcp-server-qdrant%22%5D%2C%22env%22%3A%7B%22QDRANT_URL%22%3A%22%24%7Binput%3AqdrantUrl%7D%22%2C%22QDRANT_API_KEY%22%3A%22%24%7Binput%3AqdrantApiKey%7D%22%2C%22COLLECTION_NAME%22%3A%22%24%7Binput%3AcollectionName%7D%22%7D%7D&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantUrl%22%2C%22description%22%3A%22Qdrant+URL%22%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantApiKey%22%2C%22description%22%3A%22Qdrant+API+Key%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22collectionName%22%2C%22description%22%3A%22Collection+Name%22%7D%5D&quality=insiders)

[![Install with Docker in VS Code](https://img.shields.io/badge/VS_Code-Docker-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=qdrant&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-p%22%2C%228000%3A8000%22%2C%22-i%22%2C%22--rm%22%2C%22-e%22%2C%22QDRANT_URL%22%2C%22-e%22%2C%22QDRANT_API_KEY%22%2C%22-e%22%2C%22COLLECTION_NAME%22%2C%22mcp-server-qdrant%22%5D%2C%22env%22%3A%7B%22QDRANT_URL%22%3A%22%24%7Binput%3AqdrantUrl%7D%22%2C%22QDRANT_API_KEY%22%3A%22%24%7Binput%3AqdrantApiKey%7D%22%2C%22COLLECTION_NAME%22%3A%22%24%7Binput%3AcollectionName%7D%22%7D%7D&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantUrl%22%2C%22description%22%3A%22Qdrant+URL%22%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantApiKey%22%2C%22description%22%3A%22Qdrant+API+Key%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22collectionName%22%2C%22description%22%3A%22Collection+Name%22%7D%5D) [![Install with Docker in VS Code Insiders](https://img.shields.io/badge/VS_Code_Insiders-Docker-24bfa5?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=qdrant&config=%7B%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-p%22%2C%228000%3A8000%22%2C%22-i%22%2C%22--rm%22%2C%22-e%22%2C%22QDRANT_URL%22%2C%22-e%22%2C%22QDRANT_API_KEY%22%2C%22-e%22%2C%22COLLECTION_NAME%22%2C%22mcp-server-qdrant%22%5D%2C%22env%22%3A%7B%22QDRANT_URL%22%3A%22%24%7Binput%3AqdrantUrl%7D%22%2C%22QDRANT_API_KEY%22%3A%22%24%7Binput%3AqdrantApiKey%7D%22%2C%22COLLECTION_NAME%22%3A%22%24%7Binput%3AcollectionName%7D%22%7D%7D&inputs=%5B%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantUrl%22%2C%22description%22%3A%22Qdrant+URL%22%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22qdrantApiKey%22%2C%22description%22%3A%22Qdrant+API+Key%22%2C%22password%22%3Atrue%7D%2C%7B%22type%22%3A%22promptString%22%2C%22id%22%3A%22collectionName%22%2C%22description%22%3A%22Collection+Name%22%7D%5D&quality=insiders)

#### Manual Installation

Add the following JSON block to your User Settings (JSON) file in VS Code. You can do this by pressing `Ctrl + Shift + P` and typing `Preferences: Open User Settings (JSON)`.

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "qdrantUrl",
        "description": "Qdrant URL"
      },
      {
        "type": "promptString",
        "id": "qdrantApiKey",
        "description": "Qdrant API Key",
        "password": true
      },
      {
        "type": "promptString",
        "id": "collectionName",
        "description": "Collection Name"
      }
    ],
    "servers": {
      "qdrant": {
        "command": "uvx",
        "args": ["mcp-server-qdrant"],
        "env": {
          "QDRANT_URL": "${input:qdrantUrl}",
          "QDRANT_API_KEY": "${input:qdrantApiKey}",
          "COLLECTION_NAME": "${input:collectionName}"
        }
      }
    }
  }
}
```

Or if you prefer using Docker, add this configuration instead:

```json
{
  "mcp": {
    "inputs": [
      {
        "type": "promptString",
        "id": "qdrantUrl",
        "description": "Qdrant URL"
      },
      {
        "type": "promptString",
        "id": "qdrantApiKey",
        "description": "Qdrant API Key",
        "password": true
      },
      {
        "type": "promptString",
        "id": "collectionName",
        "description": "Collection Name"
      }
    ],
    "servers": {
      "qdrant": {
        "command": "docker",
        "args": [
          "run",
          "-p", "8000:8000",
          "-i",
          "--rm",
          "-e", "QDRANT_URL",
          "-e", "QDRANT_API_KEY",
          "-e", "COLLECTION_NAME",
          "mcp-server-qdrant"
        ],
        "env": {
          "QDRANT_URL": "${input:qdrantUrl}",
          "QDRANT_API_KEY": "${input:qdrantApiKey}",
          "COLLECTION_NAME": "${input:collectionName}"
        }
      }
    }
  }
}
```

Alternatively, you can create a `.vscode/mcp.json` file in your workspace with the following content:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "qdrantUrl",
      "description": "Qdrant URL"
    },
    {
      "type": "promptString",
      "id": "qdrantApiKey",
      "description": "Qdrant API Key",
      "password": true
    },
    {
      "type": "promptString",
      "id": "collectionName",
      "description": "Collection Name"
    }
  ],
  "servers": {
    "qdrant": {
      "command": "uvx",
      "args": ["mcp-server-qdrant"],
      "env": {
        "QDRANT_URL": "${input:qdrantUrl}",
        "QDRANT_API_KEY": "${input:qdrantApiKey}",
        "COLLECTION_NAME": "${input:collectionName}"
      }
    }
  }
}
```

For workspace configuration with Docker, use this in `.vscode/mcp.json`:

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "qdrantUrl",
      "description": "Qdrant URL"
    },
    {
      "type": "promptString",
      "id": "qdrantApiKey",
      "description": "Qdrant API Key",
      "password": true
    },
    {
      "type": "promptString",
      "id": "collectionName",
      "description": "Collection Name"
    }
  ],
  "servers": {
    "qdrant": {
      "command": "docker",
      "args": [
        "run",
        "-p", "8000:8000",
        "-i",
        "--rm",
        "-e", "QDRANT_URL",
        "-e", "QDRANT_API_KEY",
        "-e", "COLLECTION_NAME",
        "mcp-server-qdrant"
      ],
      "env": {
        "QDRANT_URL": "${input:qdrantUrl}",
        "QDRANT_API_KEY": "${input:qdrantApiKey}",
        "COLLECTION_NAME": "${input:collectionName}"
      }
    }
  }
}
```

## Contributing

If you have suggestions for how mcp-server-qdrant could be improved, or want to report a bug, open an issue!
We'd love all and any contributions.

### Development Setup

For rapid iteration during development:

```bash
# Install the project in editable mode
uv pip install -e .

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run mcp-server-qdrant
```

### Publishing to PyPI

When extending or forking this project, ensure you have a unique package name:

1. **Update `pyproject.toml`** with a unique name (e.g., `mcp-server-qdrant-pro`):
   ```toml
   [project]
   name = "mcp-server-qdrant-pro"

   [project.scripts]
   mcp-server-qdrant-pro = "mcp_server_qdrant.main:main"

   [tool.hatch.build.targets.wheel]
   packages = ["src/mcp_server_qdrant"]
   ```

2. **Build the package** (requires PyPI account and API token):
   ```bash
   # Build without including source files
   uv build --no-sources
   ```

3. **Publish to PyPI**:
   ```bash
   # Note: API token must be scoped to "all projects" for first-time publishers
   uv publish --token pypi-yourtoken
   ```

### Testing `mcp-server-qdrant-pro` locally

The [MCP inspector](https://github.com/modelcontextprotocol/inspector) is the recommended tool for testing:

```bash
# Using development mode
npx @modelcontextprotocol/inspector uv run mcp-server-qdrant-pro

# For enterprise mode testing
ENTERPRISE_MODE=true COLLECTION_NAME="test" QDRANT_LOCAL_PATH="/tmp/test-storage" \
npx @modelcontextprotocol/inspector uv run mcp-server-qdrant-pro
```

## License

This MCP server is licensed under the Apache License 2.0. This means you are free to use, modify, and distribute the
software, subject to the terms and conditions of the Apache License 2.0. For more details, please see the LICENSE file
in the project repository.
