# Mem0 Agent Memory

[![PyPI version](https://img.shields.io/pypi/v/mem0-agent-memory.svg)](https://pypi.org/project/mem0-agent-memory/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/mem0-agent-memory?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/mem0-agent-memory)
[![Python versions](https://img.shields.io/pypi/pyversions/mem0-agent-memory.svg)](https://pypi.org/project/mem0-agent-memory/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP server for Mem0 agent memory management with multi-backend support.

## Features

- **Multi-backend**: FAISS (local), OpenSearch (AWS), Mem0 Platform (cloud)
- **AWS Bedrock integration**: Uses Amazon Titan embeddings and Claude 3.5 Haiku for processing
- **Auto user detection**: Uses system username when no user_id provided
- **Relevance filtering**: Returns memories with score > 0.7
- **Complete memory operations**: store, search, list, get, delete, history
- **Pagination support**: Handle large memory collections efficiently
- **Recent memory tracking**: Get latest updates for session continuity
- **Robust error handling**: Graceful fallbacks and clear error messages

## Installation

```bash
pip install mem0-agent-memory
```

## Quick Start

```bash
# Run directly with uvx
uvx mem0-agent-memory

# Or install and run
pip install mem0-agent-memory
python -m mem0_agent_memory
```

## Configuration

### AWS Configuration

For AWS Bedrock integration (used by default), ensure AWS credentials are configured:

```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-west-2"
```

### Environment Variables

```bash
# FAISS (default - uses .mem0/memory in current directory)
export FAISS_PATH="/path/to/memory/storage"  # Optional

# OpenSearch
export OPENSEARCH_HOST="your-opensearch-endpoint"
export AWS_REGION="us-west-2"

# Mem0 Platform
export MEM0_API_KEY="your-api-key"

# User/Agent ID (optional - auto-detects if not provided)
export MEM0_USER_ID="custom-user-id"      # Defaults to system username
export MEM0_AGENT_ID="custom-agent-id"    # Defaults to workspace name
```

### MCP Client Setup

#### Amazon Q CLI

Create or edit the MCP configuration file:

**Global Scope:** `~/.aws/amazonq/mcp.json`
**Local Scope:** `.amazonq/mcp.json` (project-specific)

```json
{
  "mcpServers": {
    "mem0-agent-memory": {
      "command": "uvx",
      "args": ["mem0-agent-memory"],
      "env": {
        "FAISS_PATH": "/Users/yourname/.mem0/agent",
        "MEM0_USER_ID": "john",
        "MEM0_AGENT_ID": "my-project"
      }
    }
  }
}
```

#### KIRO

Add to your KIRO MCP configuration:

```json
{
  "mcpServers": {
    "mem0-agent-memory": {
      "command": "uvx",
      "args": ["mem0-agent-memory"],
      "env": {
        "FAISS_PATH": "/Users/yourname/.mem0/agent",
        "MEM0_USER_ID": "john",
        "MEM0_AGENT_ID": "my-project"
      }
    }
  }
}
```

## Tools

- `store_memory(content, user_id?, agent_id?, metadata?)` - Store memory with metadata
- `search_memories(query, user_id?, agent_id?, limit?, page?, page_size?)` - Search with relevance filtering & pagination
- `list_memories(user_id?, agent_id?, page?, page_size?)` - List all memories with pagination
- `get_memory(memory_id)` - Get specific memory by ID
- `delete_memory(memory_id)` - Delete memory by ID (permanent)
- `get_memory_history(memory_id)` - Get change history for memory
- `get_recent_memory(days?, limit?, user_id?, agent_id?)` - Get recent memories for session continuity

## Usage Examples

### Store Memory
```json
// Auto-detect user
{"content": "User prefers React over Vue"}

// With metadata
{"content": "API endpoint changed", "metadata": {"type": "technical", "priority": "high"}}

// Specific user
{"content": "Project deadline is next Friday", "user_id": "john"}
```

### Search Memories
```json
// Basic search
{"query": "React preferences"}

// With pagination
{"query": "API endpoints", "limit": 5, "page": 2}

// Specific user
{"query": "project status", "user_id": "john"}
```

### List Memories
```json
// Auto-detect user with pagination
{"page": 1, "page_size": 10}

// Specific user
{"user_id": "john", "page": 2, "page_size": 25}
```

### Get Recent Memories
```json
// Last week (default)
{}

// Last 3 days, limit 5
{"days": 3, "limit": 5}

// Specific user
{"days": 7, "user_id": "john"}
```

### Memory Management
```json
// Get specific memory
{"memory_id": "cafdf73c-f8c7-4729-b840-e88ce7d8a67c"}

// Get memory history
{"memory_id": "cafdf73c-f8c7-4729-b840-e88ce7d8a67c"}

// Delete memory (permanent)
{"memory_id": "cafdf73c-f8c7-4729-b840-e88ce7d8a67c"}
```

## Architecture

### Backend Auto-Detection
1. **Mem0 Platform**: If `MEM0_API_KEY` is set
2. **OpenSearch**: If `OPENSEARCH_HOST` is set
3. **FAISS**: Default fallback (local storage in `.mem0/memory`)

### Auto User/Agent Detection
When neither `user_id` nor `agent_id` is provided, automatically detects:
- **`user_id`**: `MEM0_USER_ID` env var → system username
- **`agent_id`**: `MEM0_AGENT_ID` env var → workspace name (current directory)

This enables dual memories: user memories are personal, agent memories are workspace-specific.

### Relevance Filtering
Search results automatically filtered to return only memories with relevance score > 0.7, ensuring high-quality results.

### Error Handling
- Automatic fallback to `/tmp` if FAISS path is not writable
- Clear error messages for missing dependencies
- Graceful handling of network issues and invalid parameters

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use this software in your research or project, please cite it as:

```bibtex
@software{selvam_mem0_agent_memory_2024,
  author = {Selvam, Arunkumar},
  title = {Mem0 Agent Memory - MCP Server},
  url = {https://github.com/arunkumars-mf/mem0-agent-memory},
  version = {1.0.0},
  year = {2024}
}
```

## License

MIT
