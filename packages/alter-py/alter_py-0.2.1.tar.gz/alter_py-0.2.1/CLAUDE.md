# alter-py - Official Python Client SDK

## Overview
The official Python client library for the Alter AI platform, providing type-safe access to all API endpoints with both synchronous and asynchronous interfaces. This SDK enables developers to integrate Alter AI's MCP server management capabilities into their Python applications with comprehensive error handling and automatic retries.

## Key Features

- **MCP Server Management**: List, discover, and manage MCP servers (platform and external)
- **Identity Management**: Support for identities (USER, AGENT, GROUP, ORGANIZATION)
- **Authentication**: API key authentication only
- **Health Monitoring**: System health checks and monitoring
- **Async Support**: Both synchronous and asynchronous interfaces

## Quick Navigation
- **Looking for basic usage?** → Check `examples/basic_usage.py`
- **Need async examples?** → See `examples/async_usage.py`
- **Want to handle errors?** → Look at `examples/error_handling.py` and `_exceptions.py`
- **API resource implementations?** → Check `resources/` subdirectory
- **Type definitions?** → See `types/` subdirectory for all request/response models
- **HTTP client details?** → Look at `_base_client.py` for httpx implementation

## Directory Structure
```
alter-py/
├── alter/                    # Main package directory
│   ├── __init__.py          # Package exports (Alter, AsyncAlter, exceptions, types)
│   ├── _base_client.py      # HTTP client base classes with retry logic
│   ├── _client.py           # Main client classes (Client/AsyncClient) - MCP focused
│   ├── _constants.py        # Configuration constants (timeouts, URLs, limits)
│   ├── _exceptions.py       # Exception hierarchy for API errors
│   ├── _models.py           # Base Pydantic model classes
│   ├── _response.py         # Response wrapper classes (APIResponse)
│   ├── _types.py            # Type definitions and utilities
│   ├── _version.py          # Version information (__version__, __title__)
│   ├── resources/           # API endpoint implementations - MCP focused
│   │   ├── __init__.py      # Resource exports
│   │   ├── _base.py         # Base resource classes
│   │   ├── health.py        # Health check endpoints
│   │   └── mcp.py           # ✅ MCP server management and tool execution
│   └── types/               # API type definitions - MCP focused
│       ├── __init__.py      # Type exports
│       └── health.py        # Health check types
├── examples/                # MCP-focused usage examples
│   ├── basic_usage.py       # ✅ MCP server and tool usage patterns
│   ├── async_usage.py       # ✅ Async MCP operations and concurrency
│   ├── error_handling.py    # ✅ MCP-specific error handling
│   └── mcp_usage.py         # ✅ Advanced MCP patterns and LangChain integration
├── tests/                   # Test suite
│   └── test_mcp_integration.py # ✅ Comprehensive MCP integration tests
├── LICENSE                  # MIT license
├── README.md               # ✅ MCP-focused user documentation
├── pyproject.toml          # Package configuration
└── CLAUDE.md               # This documentation
```

## File Reference

### `alter/__init__.py`
**Purpose**: Package exports and public API surface - MCP focused
**Dependencies**: All internal modules

#### Key Exports:
- `Alter` / `AsyncAlter`: Main client classes (aliases for Client/AsyncClient)
- `Client` / `AsyncClient`: MCP-focused client implementations
- Exception classes: `AlterError`, `APIError`, `AuthenticationError`, etc.
- Type utilities: `NOT_GIVEN`, `Omit`, `NotGiven`, `RequestOptions`
- Response types: `APIResponse`, `AsyncAPIResponse`
- Constants: `DEFAULT_TIMEOUT`, `DEFAULT_MAX_RETRIES`

### `alter/_client.py`
**Purpose**: Main client classes that users instantiate - MCP focused
**Dependencies**: `_base_client`, `resources`, `_types`, `_constants`

#### Classes:
- `Client`
  - **Purpose**: Synchronous API client with MCP resource properties
  - **Key Methods**:
    - `__init__(api_key, base_url, timeout, ...)`: Initialize with config
    - `with_options()`: Create new client with modified options
  - **Properties**: `mcp`, `health`
  - **Usage Pattern**: `client = Alter(api_key="..."); client.mcp.list()`

- `AsyncClient`
  - **Purpose**: Asynchronous API client with async MCP resource properties
  - **Key Methods**: Same as Client but async context manager support
  - **Usage Pattern**: `async with AsyncAlter(...) as client: await client.mcp.list()`

### `alter/resources/mcp.py` ⭐ **Core Resource**
**Purpose**: MCP server management and tool execution
**Dependencies**: `_base`, `types` (auth/users/health only)

#### Classes:
- `MCPServers(BaseResource)`
  - **Purpose**: Synchronous MCP operations
  - **Key Methods**:
    - `list(limit, offset)`: List all MCP servers (platform + external)
    - `get_tools(server_id)`: Get tools from specific MCP server
    - `execute_tool(server_id, tool_name, input)`: Execute tool via MCP server
  - **Common Issues**: Remember to check if servers exist before tool execution

- `AsyncMCPServers(AsyncBaseResource)`
  - **Purpose**: Asynchronous MCP operations
  - **Key Methods**: Async versions of MCPServers methods
  - **Usage Pattern**: `result = await client.mcp.execute_tool(...)`

#### MCP Models:
- `MCPServer`: Server metadata (name, description, status, type)
- `MCPTool`: Tool definition (name, description, input_schema)
- `MCPToolExecutionResponse`: Tool execution result with success/failure


### `alter/resources/health.py`
**Purpose**: Health check endpoints
**Dependencies**: `_base`, `types.health`

#### Key Methods:
- `check()`: Basic health check
- `detailed()`: Detailed health with dependency status

## 🚧 Known Issues & TODOs
- [ ] MCP server health monitoring endpoints not yet implemented
- [ ] Streaming responses for long-running MCP tools not supported
- [ ] WebSocket support for real-time MCP server events not implemented
- [ ] Batch operations for multiple MCP tool executions needed
- [ ] Rate limit handling could be improved with backoff headers
- [ ] MCP server deployment endpoints not yet implemented in SDK

## 🧪 Testing
- **Run tests**: `pytest tests/` 
- **Type checking**: `mypy alter/`
- **Linting**: `ruff check alter/`
- **Coverage**: Current MCP integration tests provide good coverage
- **Key test files**:
  - `test_mcp_integration.py` - Comprehensive MCP server and tool testing

## 💡 Developer Notes
- SDK follows httpx patterns for HTTP client configuration
- All API responses are validated with Pydantic models
- Async client shares exact same interface as sync client
- Retry logic only applies to transient failures (timeout, connection)
- API key can be provided via argument or ALTER_API_KEY env var
- Base URL defaults to production but can be overridden for dev/staging
- All timestamps are returned as ISO 8601 strings
- Large responses are automatically paginated
- **MCP-first design**: All tool operations go through MCP servers

## Common Patterns

### MCP Server Discovery and Tool Execution
```python
from alter import Alter

client = Alter(api_key="your-key")

# Discover MCP servers
servers = client.mcp.list()
for server in servers.items:
    print(f"Server: {server.name} ({server.status})")

# Get tools from a server
if servers.items:
    tools = client.mcp.get_tools(servers.items[0].id)
    for tool in tools:
        print(f"Tool: {tool.name} - {tool.description}")

# Execute a tool
if tools:
    result = client.mcp.execute_tool(
        server_id=servers.items[0].id,
        tool_name=tools[0].name,
        input={"parameter": "value"}
    )
    print(f"Success: {result.success}, Result: {result.result}")
```

### Error Handling for MCP Operations
```python
try:
    result = client.mcp.execute_tool(server_id, tool_name, input)
except AuthenticationError:
    # Handle auth failure - check API key
except NotFoundError as e:
    if "server" in str(e).lower():
        # MCP server not found
    else:
        # Tool not found in server
except BadRequestError as e:
    # Invalid input parameters for MCP tool
except APIError as e:
    # Other API errors (MCP server issues, etc.)
```

### Async MCP Operations
```python
async with AsyncAlter(api_key="your-key") as client:
    # Concurrent server discovery
    servers = await client.mcp.list()
    
    # Get tools from multiple servers concurrently
    tool_tasks = [client.mcp.get_tools(s.id) for s in servers.items]
    all_tools = await asyncio.gather(*tool_tasks, return_exceptions=True)
    
    # Execute tools concurrently
    execution_tasks = []
    for server, tools in zip(servers.items, all_tools):
        if not isinstance(tools, Exception) and tools:
            task = client.mcp.execute_tool(
                server_id=server.id,
                tool_name=tools[0].name,
                input={"test": "data"}
            )
            execution_tasks.append(task)
    
    results = await asyncio.gather(*execution_tasks, return_exceptions=True)
```

## Configuration

### Environment Variables
```bash
ALTER_API_KEY=your-api-key       # API authentication
ALTER_LOG=debug                  # Enable debug logging
```

### Client Options
- `api_key`: Authentication key (required)
- `base_url`: API base URL (default: production)
- `timeout`: Request timeout in seconds or httpx.Timeout
- `max_retries`: Number of retry attempts (default: 3)
- `custom_headers`: Additional headers for all requests
- `custom_query`: Additional query params for all requests
- `proxies`: Dict or httpx proxy configuration
- `verify`: SSL verification (bool, str path, or SSLContext)

## Integration Points
- **API Service**: Communicates with services/api/ at base_url
- **Authentication**: Bearer token in Authorization header
- **MCP Operations**: POST /mcp/servers/{id}/tools/{name}/execute endpoint
- **Error Responses**: Standardized error format with code/message

## Debugging Guide
- **Network issues** → Check proxies configuration, verify SSL settings
- **Auth failures** → Verify API key is correct and not expired
- **MCP server not found** → Check server ID, verify server is deployed
- **Tool not found** → Check tool name, verify server has that tool
- **Timeout errors** → Increase timeout, check if MCP server is slow
- **Parse errors** → Enable debug logging to see raw responses
- **Import errors** → Ensure all dependencies installed with pip

## Performance Considerations
- HTTP keep-alive enabled by default via httpx
- Connection pooling with configurable limits
- Automatic retry with exponential backoff
- Response parsing uses Pydantic's optimized validators
- Large responses should use pagination parameters
- MCP operations may be slower than direct API calls (server overhead)

## Security Considerations
- API key should never be hardcoded
- Use environment variables or secure key management
- SSL verification enabled by default
- Sensitive data not logged even in debug mode
- MCP server execution is sandboxed by the platform

## Migration from Native Tools
**If upgrading from a version that supported native tools:**

### Old Pattern (NO LONGER SUPPORTED):
```python
# ❌ This no longer works
result = client.tools.execute(tool_name="Math.Add", input={"a": 1, "b": 2})
```

### New MCP Pattern:
```python
# ✅ Use this instead
servers = client.mcp.list()
math_server = next(s for s in servers.items if "math" in s.name.lower())
result = client.mcp.execute_tool(
    server_id=math_server.id,
    tool_name="add",  # Tool name within the MCP server
    input={"a": 1, "b": 2}
)
```

## 🔗 Related Documentation
- Parent: `../CLAUDE.md` (workspace root)
- API Service: `../services/api/CLAUDE.md`
- Main Platform: `../alter-ai/` repository
- MCP Documentation: https://modelcontextprotocol.io/
- API Docs: https://docs.alter.ai/api

## 🚨 **CRITICAL NOTES FOR CLAUDE**

1. **MCP-Only Architecture**: This SDK only supports MCP-based tool execution
2. **No Native Tools**: Never suggest `client.tools.*` patterns - they don't exist
3. **Always Use MCP Pattern**: `client.mcp.list()` → `client.mcp.get_tools()` → `client.mcp.execute_tool()`
4. **Server-First Thinking**: Users must have MCP servers deployed before executing tools
5. **Async Best Practices**: MCP operations benefit greatly from async/concurrent patterns
6. **Error Handling**: MCP introduces server-level errors that don't exist in native tools
7. **Examples are Authoritative**: Use `examples/` files as canonical usage patterns

This SDK is designed for the modern Alter AI platform architecture where all tools are accessed through MCP servers.