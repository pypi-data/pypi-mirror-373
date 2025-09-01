# Memory Graph MCP Server for Python Development

A specialized MCP server that tracks your Python development sessions, errors, fixes, and coding patterns using a persistent knowledge graph. This helps you build a searchable database of your development learnings, solutions, and insights.

## Usage with Visual Studio Code

### Setup

Add this to your `mcp.json` (you need to have uv installed):

#### UVX (Recommended)
```json
{
    "servers": {
        "agentmemory": {
            "command": "uvx",
            "args": [
                "mcp-agentmemory",
                "--memory-file-path",
                "<directory where to story your memories, default ~/.mcp/>"
            ]
        }
    }
}
```

The server creates two files in the specified directory:
- `agentmemory.json`: Snapshot of the current knowledge graph
- `agentmemory.log.jsonl`: Append-only event log for durability


## Core Concepts

### Entities
Entities represent the building blocks of your development knowledge:
- **Features**: Projects or tasks you're working on
- **Sessions**: Individual development work periods
- **Errors**: Persistent error tracking with fingerprinting
- **Patterns**: Reusable solutions and coding patterns
- **Modules/Classes/Functions**: Code structure elements

Example:
```json
{
  "name": "user-authentication",
  "entityType": "Feature",
  "tags": ["backend", "security"],
  "description": "JWT-based user authentication system"
}
```

### Relations
Relations connect your development knowledge to show how different pieces relate:
- `implements`: A session implements a feature
- `encounters`: A feature encounters an error
- `fixed_by`: An error is fixed by a pattern
- `depends_on`: Dependencies between modules/features

Example:
```json
{
  "from": "session:abc123",
  "to": "user-authentication",
  "relationType": "implements"
}
```

### Observations
Observations store your actual development insights and knowledge:
- **note**: General observations and learnings
- **snippet**: Code examples and implementations
- **error**: Exception details and stack traces
- **command**: CLI commands and scripts
- **qa**: Questions, answers, and troubleshooting

Example:
```json
{
  "kind": "snippet",
  "text": "JWT token validation middleware",
  "code": "def validate_jwt(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY)",
  "language": "python",
  "tags": ["jwt", "middleware", "auth"]
}
```

## API Tools

### Core Knowledge Management
- **upsert_entity**: Create or update entities (features, patterns, concepts)
- **create_relations**: Establish connections between entities
- **add_insights**: Store observations and code snippets
- **read_graph**: Retrieve the complete knowledge graph
- **search_insights**: Search through insights by text, tags, kind, or language

### Development Session Tracking
- **start_session**: Begin a tracked development session for a feature
- **log_event**: Record development activities, decisions, and code during a session
- **end_session**: Complete a session with a summary of outcomes

### Error and Solution Management
- **record_error**: Create persistent error entities with automatic fingerprinting
- **record_fix**: Attach solutions to errors and create reusable patterns

### Export and Maintenance
- **export_markdown**: Generate comprehensive documentation from your knowledge graph
- **compact_store**: Optimize storage by creating snapshots and clearing logs



## System Prompt for Development

Use this prompt to optimize the memory server for development work:

```
You are a development assistant with persistent memory. Follow these steps:

1. Session Management:
   - Start sessions when beginning focused development work
   - Log significant code changes, decisions, and learnings
   - Record errors and their solutions for future reference

2. Knowledge Capture:
   - Store useful code snippets with proper tagging
   - Document architectural decisions and trade-offs
   - Record debugging approaches and troubleshooting steps
   - Capture CLI commands and development workflows

3. Pattern Recognition:
   - Identify recurring solutions and create reusable patterns
   - Link related errors to their fixes
   - Build connections between similar technical concepts

4. Search and Retrieval:
   - Search previous solutions when encountering similar problems
   - Reference past sessions for context on ongoing features
   - Use tags and entity relationships to find relevant knowledge
```

## Storage and Persistence

The server uses a dual storage approach:
- **Snapshot file**: Complete knowledge graph state for fast loading
- **Event log**: Append-only log of all changes for durability and replay

Use `compact_store` periodically to optimize storage by creating fresh snapshots and clearing the event log.

## License

This MCP server is licensed under the MIT License. You are free to use, modify, and distribute the software under the terms of the MIT License.
