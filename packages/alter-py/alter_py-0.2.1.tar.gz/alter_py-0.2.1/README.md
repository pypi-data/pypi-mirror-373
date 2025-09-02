# Alter Python Client

[![PyPI version](https://img.shields.io/pypi/v/alter-py.svg)](https://pypi.org/project/alter-py/)
[![Python versions](https://img.shields.io/pypi/pyversions/alter-py.svg)](https://pypi.org/project/alter-py/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The Alter Python library provides convenient access to the Alter AI API from any Python 3.11+ 
application. The library includes type definitions for all request params and response fields,
and offers both synchronous and asynchronous clients powered by [httpx](https://github.com/encode/httpx).

## Installation

```sh
# Install from PyPI
pip install alter-py
```

## Usage

The Alter platform uses **MCP (Model Context Protocol) servers** to provide tools. This means all tool execution happens through deployed MCP servers rather than direct tool calls.

### Basic MCP Usage

```python
import os
from alter import Alter

client = Alter(
    api_key=os.environ.get("ALTER_API_KEY"),  # This is the default and can be omitted
)

# List available MCP servers
servers = client.mcp.list()
print(f"Available servers: {len(servers)}")

# Get tools from a specific server
if servers:
    first_server = servers[0]
    tools = client.mcp.get_tools(first_server.id)
    print(f"Tools in {first_server.name}: {len(tools)}")
    
    # Execute a tool from the MCP server
    if tools:
        result = client.mcp.execute_tool(
            server_id=first_server.id,
            tool_name=tools[0].name,
            input={"message": "Hello from Alter Python SDK!"}
        )
        print(f"Result: {result}")
```

While you can provide an `api_key` keyword argument, we recommend using 
[python-dotenv](https://pypi.org/project/python-dotenv/) to add `ALTER_API_KEY="My API Key"` 
to your `.env` file so that your API Key is not stored in source control.

## Async Usage

Simply import `AsyncAlter` instead of `Alter` and use `await` with each API call:

```python
import os
import asyncio
from alter import AsyncAlter

async def main():
    async with AsyncAlter(api_key=os.environ.get("ALTER_API_KEY")) as client:
        # List MCP servers
        servers = await client.mcp.list()
        
        if not servers:
            print("No MCP servers found. Deploy some servers first!")
            return
        
        # Get tools from multiple servers concurrently
        tool_tasks = [
            client.mcp.get_tools(server.id) 
            for server in servers
        ]
        
        all_server_tools = await asyncio.gather(*tool_tasks, return_exceptions=True)
        
        # Execute tools concurrently
        execution_tasks = []
        for i, tools in enumerate(all_server_tools):
            if isinstance(tools, Exception) or not tools:
                continue
            
            server = servers[i]
            task = client.mcp.execute_tool(
                server_id=server.id,
                tool_name=tools[0].name,
                input={"message": f"Hello from {server.name}!"}
            )
            execution_tasks.append((server, tools[0], task))
        
        # Wait for all executions
        results = await asyncio.gather(
            *[task for _, _, task in execution_tasks],
            return_exceptions=True
        )
        
        # Display results
        for i, result in enumerate(results):
            server, tool, _ = execution_tasks[i]
            if isinstance(result, Exception):
                print(f"❌ {server.name}.{tool.name}: {result}")
            else:
                print(f"✅ {server.name}.{tool.name}: Success")

asyncio.run(main())
```

Functionality between the synchronous and asynchronous clients is otherwise identical.

## MCP Server Management

The SDK provides comprehensive MCP server management capabilities:

```python
from alter import Alter

client = Alter()

# List all MCP servers (both platform and external)
all_servers = client.mcp.list()

# Filter by server type
for server in all_servers:
    server_type = "🐳 Platform" if hasattr(server, 'deployment_status') else "🔗 External"
    print(f"{server_type} - {server.name}: {getattr(server, 'status', 'Unknown')}")

# Get detailed server information
if all_servers:
    server_id = all_servers[0].id
    
    # Get all tools from this server
    tools = client.mcp.get_tools(server_id)
    
    for tool in tools:
        print(f"📋 {tool.name}: {tool.description or 'No description'}")
        if hasattr(tool, 'input_schema'):
            print(f"   Input schema: {tool.input_schema}")
```


## Using Types

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). 
Responses are [Pydantic models](https://docs.pydantic.dev) which also provide helper methods for things like:

- Serializing back into JSON: `model.model_dump_json()`
- Converting to a dictionary: `model.model_dump()`

Typed requests and responses provide autocomplete and documentation within your editor. 
If you would like to see type errors in VS Code to help catch bugs earlier, 
set `python.analysis.typeCheckingMode` to `basic`.

## Handling Errors

When the library is unable to connect to the API (for example, due to network connection problems 
or a timeout), a subclass of `alter.APIConnectionError` is raised.

When the API returns a non-success status code (that is, 4xx or 5xx response), a subclass of 
`alter.APIStatusError` is raised, containing `status_code` and `response` properties.

All errors inherit from `alter.APIError`.

```python
import alter
from alter import Alter

client = Alter()

try:
    # Try to get tools from a non-existent MCP server
    tools = client.mcp.get_tools("non-existent-server-id")
except alter.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx.
except alter.NotFoundError as e:
    print("MCP server not found - check server ID")
    print(e.status_code)
except alter.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except alter.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

### MCP-Specific Error Handling

```python
try:
    # List servers
    servers = client.mcp.list()
    
    if not servers:
        print("❌ No MCP servers available - deploy some servers first!")
        return
    
    # Execute tool
    server = servers[0]
    tools = client.mcp.get_tools(server.id)
    
    if tools:
        result = client.mcp.execute_tool(
            server_id=server.id,
            tool_name=tools[0].name,
            input={"message": "test"}
        )
        print(f"✅ Execution successful")

except alter.AuthenticationError:
    print("❌ Please check your API key")
except alter.NotFoundError as e:
    if "server" in str(e).lower():
        print("❌ MCP server not found - check server ID")
    else:
        print("❌ Tool not found - check the tool name")
except alter.BadRequestError as e:
    print(f"❌ Invalid MCP request: {e}")
    print("   Check your input parameters and server configuration")
except alter.APITimeoutError:
    print("❌ Request timed out - MCP server may be slow or overloaded")
```

Error codes are as follows:

| Status Code | Error Type                 |
| ----------- | -------------------------- |
| 400         | `BadRequestError`          |
| 401         | `AuthenticationError`      |
| 403         | `PermissionDeniedError`    |
| 404         | `NotFoundError`            |
| 422         | `UnprocessableEntityError` |
| 429         | `RateLimitError`           |
| >=500       | `InternalServerError`      |
| N/A         | `APIConnectionError`       |

### Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff.
Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 
409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable retry settings:

```python
from alter import Alter

# Configure the default for all requests:
client = Alter(
    # default is 2
    max_retries=0,
)

# Or, configure per-request:
servers = client.with_options(max_retries=5).mcp.list()
```

### Timeouts

By default requests time out after 1 minute. You can configure this with a `timeout` option,
which accepts a float or an [`httpx.Timeout`](https://www.python-httpx.org/advanced/#fine-tuning-the-configuration) object:

```python
from alter import Alter
import httpx

# Configure the default for all requests:
client = Alter(
    # 20 seconds (default is 1 minute)
    timeout=20.0,
)

# More granular control:
client = Alter(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
servers = client.with_options(timeout=5.0).mcp.list()
```

On timeout, an `APITimeoutError` is thrown.

Note that requests that time out are [retried twice by default](#retries).

## Advanced

### Logging

We use the standard library [`logging`](https://docs.python.org/3/library/logging.html) module.

You can enable logging by setting the environment variable `ALTER_LOG` to `info`.

```shell
$ export ALTER_LOG=info
```

Or to `debug` for more verbose logging.

### How to tell whether `None` means `null` or missing

In an API response, a field may be explicitly `null`, or missing entirely; in either case, 
its value is `None` in this library. You can differentiate the two cases with `.model_fields_set`:

```py
if response.my_field is None:
  if 'my_field' not in response.model_fields_set:
    print('Got json like {}, without a "my_field" key present at all.')
  else:
    print('Got json like {"my_field": null}.')
```

### Accessing raw response data (e.g. headers)

The "raw" Response object can be accessed by prefixing `.with_raw_response.` to any HTTP method call, e.g.,

```py
from alter import Alter

client = Alter()

# Get raw response from MCP operation
servers = client.mcp.list()
if servers:
    response = client.mcp.with_raw_response().execute_tool(
        server_id=servers[0].id,
        tool_name="example_tool",
        input={"test": "data"}
    )
    
    print(response.headers.get('X-Request-ID'))
    print(f"Status: {response.status_code}")
    
    # Parse the actual result
    execution = response.parse()  # get the object that `mcp.execute_tool()` would have returned
    print(f"Result: {execution}")
```

These methods return an [`APIResponse`](https://github.com/alter-ai/alter-py/tree/main/alter/_response.py) object.

The async client returns an [`AsyncAPIResponse`](https://github.com/alter-ai/alter-py/tree/main/alter/_response.py) 
with the same structure, the only difference being `await`able methods for reading the response content.

## Examples

Check out the `examples/` directory for more comprehensive usage patterns:

- `examples/basic_usage.py` - Basic MCP server and tool usage
- `examples/async_usage.py` - Async patterns and concurrent operations  
- `examples/error_handling.py` - Comprehensive error handling for MCP operations
- `examples/mcp_usage.py` - Advanced MCP patterns and LangChain integration

## Requirements

Python 3.11 or higher.

## Getting Started

1. **Deploy MCP Servers**: Use the Alter dashboard to deploy MCP servers (either from templates or external servers)
2. **Get API Key**: Generate an API key from your Alter dashboard
3. **Install SDK**: `pip install alter-py`
4. **Start Building**: Use the examples above to start executing tools via MCP servers

## Contributing

See [the contributing documentation](./CONTRIBUTING.md).