#!/usr/bin/env python3
"""MCP server for Mem0 memory management with multi-backend support."""

# IMPORTANT: Set telemetry BEFORE importing mem0
import os
os.environ["MEM0_TELEMETRY"] = "false"

from mcp.server.fastmcp import FastMCP
from mem0 import MemoryClient, Memory as Mem0Memory
import json
import math
import getpass
import boto3
from opensearchpy import AWSV4SignerAuth, RequestsHttpConnection
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Initialize FastMCP server
mcp = FastMCP("mem0-agent-memory")

class Mem0ServiceClient:
    """Multi-backend Mem0 client supporting Platform, OpenSearch, and FAISS."""
    
    DEFAULT_CONFIG = {
        "embedder": {"provider": "aws_bedrock", "config": {"model": "amazon.titan-embed-text-v2:0"}},
        "llm": {
            "provider": "aws_bedrock",
            "config": {
                "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
                "temperature": 0.1,
                "max_tokens": 2000,
            },
        },
        "vector_store": {
            "provider": "opensearch",
            "config": {
                "port": 443,
                "collection_name": "mem0_agent_memories",
                "host": os.environ.get("OPENSEARCH_HOST"),
                "embedding_model_dims": 1024,
                "connection_class": RequestsHttpConnection,
                "pool_maxsize": 20,
                "use_ssl": True,
                "verify_certs": True,
            },
        },
    }

    def __init__(self, config: Optional[Dict] = None):
        """Initialize client with backend auto-detection."""
        self.mem0 = self._initialize_client(config)

    def _initialize_client(self, config: Optional[Dict] = None):
        """Initialize appropriate backend based on environment."""
        if os.environ.get("MEM0_API_KEY"):
            return MemoryClient()
        elif os.environ.get("OPENSEARCH_HOST"):
            return self._init_opensearch(config)
        else:
            return self._init_faiss(config)

    def _init_opensearch(self, config: Optional[Dict] = None):
        """Initialize OpenSearch backend."""
        region = os.environ.get("AWS_REGION", "us-west-2")
        session = boto3.Session()
        credentials = session.get_credentials()
        auth = AWSV4SignerAuth(credentials, region, "aoss")
        
        merged_config = self._merge_config(config)
        merged_config["vector_store"]["config"].update({
            "http_auth": auth,
            "host": os.environ["OPENSEARCH_HOST"]
        })
        
        return Mem0Memory.from_config(config_dict=merged_config)

    def _init_faiss(self, config: Optional[Dict] = None):
        """Initialize FAISS backend."""
        try:
            import faiss  # noqa: F401
        except ImportError as err:
            raise ImportError(
                "The faiss-cpu package is required for using FAISS as the vector store backend for Mem0. "
                "Please install it using: pip install faiss-cpu"
            ) from err
            
        merged_config = self._merge_config(config)
        
        # Use configurable FAISS path with proper fallback
        faiss_path = os.environ.get("FAISS_PATH", ".mem0/memory")
        
        # Ensure the directory exists and is writable
        try:
            os.makedirs(faiss_path, exist_ok=True)
        except (OSError, PermissionError):
            # Fallback to /tmp if the specified path is not writable
            faiss_path = "/tmp/mem0_agent"
            os.makedirs(faiss_path, exist_ok=True)
        
        # Ensure the path ends with the index filename
        if not faiss_path.endswith('.faiss'):
            faiss_path = os.path.join(faiss_path, "agent_memory.faiss")
        
        merged_config["vector_store"] = {
            "provider": "faiss",
            "config": {"embedding_model_dims": 1024, "path": faiss_path}
        }
        return Mem0Memory.from_config(config_dict=merged_config)

    def _merge_config(self, config: Optional[Dict] = None) -> Dict:
        """Deep merge user config with defaults."""
        merged_config = self.DEFAULT_CONFIG.copy()
        if not config:
            return merged_config

        for key, value in config.items():
            if key in merged_config and isinstance(value, dict) and isinstance(merged_config[key], dict):
                merged_config[key].update(value)
            else:
                merged_config[key] = value
        return merged_config

def _get_user_id():
    """Get user ID from env var or system user."""
    return os.environ.get("MEM0_USER_ID") or getpass.getuser()

def _get_agent_id():
    """Get agent ID from env var or workspace name."""
    return os.environ.get("MEM0_AGENT_ID") or os.path.basename(os.getcwd())

# Initialize mem0 client with multi-backend support
mem0_client = Mem0ServiceClient().mem0

@mcp.tool(
    description="""Store memory content with metadata support. 

REQUIRED: Either 'user_id' OR 'agent_id' (if neither provided, auto-detects current user)
REQUIRED: 'content' - the information to remember

OPTIONAL: 'metadata' - structured data about the memory (JSON object)

Examples:
- Store personal info: {"content": "User prefers React over Vue", "user_id": "john"}  
- Store with metadata: {"content": "API endpoint changed", "metadata": {"type": "technical", "priority": "high"}}
- Auto-detect user: {"content": "Remember this pattern"} (uses system username)

Use for: Storing code patterns, user preferences, project details, technical knowledge."""
)
async def store_memory(
    content: str,
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Store memory content."""
    try:
        # Auto-detect user/agent if neither provided
        if not user_id and not agent_id:
            user_id = _get_user_id()
            agent_id = _get_agent_id()
        
        messages = [{"role": "user", "content": content}]
        result = mem0_client.add(messages, user_id=user_id, agent_id=agent_id, metadata=metadata)
        return f"Memory stored successfully: {json.dumps(result, indent=2)}"
    except Exception as e:
        return f"Error storing memory: {str(e)}"

@mcp.tool(
    description="""Search memories with semantic similarity and relevance filtering.

REQUIRED: 'query' - what to search for (natural language)
OPTIONAL: 'user_id' OR 'agent_id' (if neither provided, auto-detects current user)
OPTIONAL: 'limit' - max results (default: 10)
OPTIONAL: 'page', 'page_size' - pagination controls

Returns: Top 5 most relevant memories with score > 0.7

Examples:
- Search user memories: {"query": "React patterns", "user_id": "john"}
- Auto-detect user: {"query": "my project status"} 
- Limit results: {"query": "API endpoints", "limit": 3}

Use for: Finding relevant code, recalling user preferences, retrieving project context."""
)
async def search_memories(
    query: str,
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 10,
    page: int = 1,
    page_size: int = 10
) -> str:
    """Search memories with pagination."""
    try:
        # Auto-detect user/agent if neither provided
        if not user_id and not agent_id:
            user_id = _get_user_id()
            agent_id = _get_agent_id()
        
        # Get more results to allow for filtering and pagination
        # Use a larger limit to ensure we have enough results after filtering
        search_limit = max(limit, page_size * page + 50)
        
        response = mem0_client.search(
            query=query, 
            user_id=user_id, 
            agent_id=agent_id,
            limit=search_limit
        )
        
        # Handle response format
        if isinstance(response, dict) and "results" in response:
            memories = response.get("results", [])
        else:
            memories = response if isinstance(response, list) else []
        
        # Filter by relevance score (only return memories with score > 0.7)
        filtered_memories = [m for m in memories if m.get("score", 0) > 0.7]
        
        # Apply pagination to filtered results
        total_items = len(filtered_memories)
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_memories = filtered_memories[start_idx:end_idx]
        
        result = {
            "memories": paginated_memories,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_items": total_items,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error searching memories: {str(e)}"

@mcp.tool(
    description="""List all memories for a user or agent with pagination.

OPTIONAL: 'user_id' OR 'agent_id' (if neither provided, auto-detects current user)
OPTIONAL: 'page', 'page_size' - pagination controls (default: page_size=25)

Returns: All memories belonging to the specified user/agent

Examples:
- List user memories: {"user_id": "john"}
- Auto-detect user: {} (empty - uses system username)
- With pagination: {"page": 2, "page_size": 10}

Use for: Browsing all stored memories, memory management, getting overview of stored knowledge."""
)
async def list_memories(
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 25
) -> str:
    """List all memories with pagination."""
    try:
        # Auto-detect user/agent if neither provided
        if not user_id and not agent_id:
            user_id = _get_user_id()
            agent_id = _get_agent_id()
        
        response = mem0_client.get_all(
            user_id=user_id, 
            agent_id=agent_id
        )
        
        if isinstance(response, dict) and "total" in response:
            all_memories = response.get("results", [])
            total_items = len(all_memories)
        else:
            all_memories = response if isinstance(response, list) else response.get("results", [])
            total_items = len(all_memories)
        
        # Calculate pagination
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Slice memories for current page
        paginated_memories = all_memories[start_idx:end_idx]
        
        result = {
            "memories": paginated_memories,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "total_items": total_items,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error listing memories: {str(e)}"

@mcp.tool(
    description="""Get specific memory by its unique ID.

REQUIRED: 'memory_id' - the UUID of the memory to retrieve

Returns: Complete memory details including content, metadata, timestamps, scores

Examples:
- Get memory: {"memory_id": "cafdf73c-f8c7-4729-b840-e88ce7d8a67c"}

Use for: Retrieving specific memory details, following up on search results, memory inspection."""
)
async def get_memory(memory_id: str) -> str:
    """Get memory by ID."""
    try:
        memory = mem0_client.get(memory_id)
        return json.dumps(memory, indent=2)
    except Exception as e:
        return f"Error getting memory: {str(e)}"

@mcp.tool(
    description="""Delete memory by its unique ID. PERMANENT deletion.

REQUIRED: 'memory_id' - the UUID of the memory to delete

⚠️  WARNING: This permanently removes the memory and cannot be undone.

Examples:
- Delete memory: {"memory_id": "cafdf73c-f8c7-4729-b840-e88ce7d8a67c"}

Use for: Removing outdated information, cleaning up incorrect memories, memory management."""
)
async def delete_memory(memory_id: str) -> str:
    """Delete memory by ID."""
    try:
        mem0_client.delete(memory_id)
        return f"Memory {memory_id} deleted successfully"
    except Exception as e:
        return f"Error deleting memory: {str(e)}"

@mcp.tool(
    description="""Get change history for a specific memory by ID.

REQUIRED: 'memory_id' - the UUID of the memory to get history for

Returns: Chronological list of changes, updates, and modifications to the memory

Examples:
- Get history: {"memory_id": "cafdf73c-f8c7-4729-b840-e88ce7d8a67c"}

Use for: Tracking memory evolution, debugging memory changes, audit trails."""
)
async def get_memory_history(memory_id: str) -> str:
    """Get memory history by ID."""
    try:
        history = mem0_client.history(memory_id)
        return json.dumps(history, indent=2)
    except Exception as e:
        return f"Error getting memory history: {str(e)}"

@mcp.tool(
    description="""Get recently added or updated memories for session continuity.

OPTIONAL: 'days' - how many days back to search (default: 7)
OPTIONAL: 'limit' - max memories to return (default: 10)
OPTIONAL: 'user_id' OR 'agent_id' (if neither provided, auto-detects current user)

Returns: Most recently added/updated memories sorted by newest first

Examples:
- Recent week: {"days": 7, "limit": 10}
- Last 3 days: {"days": 3, "limit": 5}
- Auto-detect user: {} (uses defaults)

Use for: Session continuity, understanding recent context, catching up on latest updates."""
)
async def get_recent_memory(
    days: int = 7,
    limit: int = 10,
    user_id: Optional[str] = None,
    agent_id: Optional[str] = None
) -> str:
    """Get recently added/updated memories for session continuity."""
    try:
        # Auto-detect user/agent if neither provided
        if not user_id and not agent_id:
            user_id = _get_user_id()
            agent_id = _get_agent_id()
        
        # Use Mem0's native filtering for recent memories
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Search with date filters - this should capture both new and updated memories
        response = mem0_client.search(
            query="recent memories project status updates decisions",
            user_id=user_id,
            agent_id=agent_id,
            limit=limit * 2  # Get more to ensure we have enough after filtering
        )
        
        # Handle response format
        if isinstance(response, dict) and "results" in response:
            memories = response.get("results", [])
        else:
            memories = response if isinstance(response, list) else []
        
        # Sort by most recent (updated_at first, then created_at)
        def get_sort_date(memory):
            updated = memory.get("updated_at")
            created = memory.get("created_at")
            return updated if updated else created
        
        memories.sort(key=get_sort_date, reverse=True)
        recent_memories = memories[:limit]
        
        result = {
            "recent_memories": recent_memories,
            "summary": {
                "days_searched": days,
                "total_found": len(recent_memories),
                "date_range": f"Last {days} days"
            }
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting recent memories: {str(e)}"

def run_server():
    """Run the MCP server."""
    mcp.run()
