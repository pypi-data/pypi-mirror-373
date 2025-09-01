# MCP Memory System

A Model Context Protocol (MCP) server that provides enhanced file system management capabilities with agent-based workspace isolation for Large Language Models (LLMs).

## Features

- **Agent-Based Workspace Management**: Multi-agent support with isolated workspace permissions
- **File Operations**: Read, write, edit, and create files with enhanced safety checks
- **Directory Management**: Create and list directories with permission controls
- **Concurrent Safe Editing**: File locking mechanism to prevent concurrent edit conflicts
- **Media File Protection**: Prevents reading of binary files (images, videos, PDFs, etc.)
- **UTF-8 Validation**: Ensures file encoding integrity
- **Workspace Isolation**: All operations are strictly restricted to agent-specific workspace directories
- **Permission System**: Granular read/write permissions per agent with directory-level access control

## Tools Provided

### Agent Management Tools
- `register_agent`: Register an agent with automatic workspace setup (creates directory with read/write access)
- `register_agent_workspace`: Register or update an agent's workspace with custom readable and writable directory paths
- `update_agent_workspace`: Add new readable and writable directory paths to an existing agent's workspace
- `get_agent_workspace`: Get workspace configuration information for a specific agent

### File System Tools
- `write_memory_file`: Create or overwrite files with automatic directory creation (requires agent registration)
- `edit_memory_file`: Edit existing files with multiple find-and-replace operations (requires agent registration)
- `read_multiple_memory_files`: Read multiple text files at once (requires agent registration)
- `create_memory_directory`: Create directories with automatic parent creation (requires agent registration)
- `list_memory_directory`: List directory contents (requires agent registration)
- `move_memory_file`: Move or rename files (requires agent registration)
- `get_memory_files`: Get all file paths in the workspace directory with unified format output

## Usage

### 1. Agent Registration (Required)

Before performing any file operations, agents must be registered:

```python
# Simple registration - creates agent workspace directory automatically
register_agent(agent_name="my_agent", agent_workspace="my_agent")

# Or advanced registration with custom paths
register_agent_workspace(
    agent_name="my_agent",
    readable_paths=["shared_data", "my_agent"],
    writable_paths=["my_agent", "output"]
)
```

### 2. File Operations

All file operations require the `agent_name` parameter and respect the agent's workspace permissions:

```python
# Write a file
write_memory_file(agent_name="my_agent", path="my_agent/data.txt", content="Hello World")

# Read multiple files
read_multiple_memory_files(agent_name="my_agent", paths=["my_agent/data.txt", "shared_data/config.json"])

# Edit a file
edit_memory_file(
    agent_name="my_agent",
    path="my_agent/data.txt",
    edits=[{"oldText": "Hello", "newText": "Hi"}]
)
```

## Installation

```bash
# Install with uv
uv add mcp-memory-system

# Or install with pip
pip install mcp-memory-system
```

## Server Configuration

### Using with MCP clients

Add the following configuration to your MCP settings:

```json
{
  "mcpServers": {
    "memory-system": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-memory-system", "run", "mcp-memory-system"],
      "env": {}
    }
  }
}
```

### Configuration Options

- `--workspace-path`: Set the workspace directory (default: ./workspace)

## Permission System

The server implements a comprehensive permission system:

- **Agent Registration Required**: All agents must be registered before performing any memory operations
- **Directory-Level Permissions**: Permissions are granted at the directory level, not individual files
- **Read/Write Separation**: Agents can have different read and write permissions
- **Workspace Isolation**: Each agent can only access files within their permitted directories
- **Automatic Directory Creation**: Directories are created automatically when agents are registered

### Permission Examples

```python
# Agent can read from "shared" and "agent1" directories, write to "agent1" only
register_agent_workspace(
    agent_name="agent1",
    readable_paths=["shared", "agent1"],
    writable_paths=["agent1"]
)

# Add additional permissions to existing agent
update_agent_workspace(
    agent_name="agent1",
    additional_readable_paths=["public_data"],
    additional_writable_paths=["output"]
)
```

## Safety Features

- **Agent-Based Access Control**: Each agent can only access files within their permitted workspace directories
- **File Type Filtering**: Automatically blocks operations on binary files (images, videos, PDFs, etc.)
- **Concurrent Access Control**: File-level locking prevents data corruption during edits
- **Strict Workspace Sandboxing**: All operations are contained within the specified workspace directory
- **Path Validation**: Prevents directory traversal attacks with "../" path components
- **UTF-8 Validation**: Ensures text file integrity after operations
- **Permission Validation**: All operations validate agent permissions before execution

## Error Handling

The server provides detailed error messages for permission violations, including:
- Current agent permissions
- Specific paths that caused the error
- Suggestions for resolving permission issues

## License

MIT License - see LICENSE file for details.