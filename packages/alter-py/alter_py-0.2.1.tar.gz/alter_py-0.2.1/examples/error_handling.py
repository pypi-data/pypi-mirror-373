"""Error handling examples for the Alter Python client using MCP servers."""

import os
from alter import (
    Alter,
    AlterError,
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    BadRequestError,
)

def main():
    # Initialize client
    client = Alter(api_key=os.environ.get("ALTER_API_KEY"))
    
    # Example 1: Handle authentication errors
    print("🔐 Testing authentication error handling...")
    try:
        # Use invalid API key
        bad_client = Alter(api_key="invalid-key")
        servers = bad_client.mcp.list()
    except AuthenticationError as e:
        print(f"  ❌ Authentication failed: {e}")
        print(f"  Status code: {e.status_code}")
    
    # Example 2: Handle server not found errors  
    print(f"\n🔍 Testing server not found error handling...")
    try:
        # Try to get tools from a non-existent MCP server
        tools = client.mcp.get_tools("non-existent-server-id")
    except NotFoundError as e:
        print(f"  ❌ MCP server not found: {e}")
        print(f"  Status code: {e.status_code}")
    
    # Example 3: Handle tool not found errors
    print(f"\n🛠️  Testing tool not found error handling...")
    try:
        # Get valid servers first
        servers = client.mcp.list(limit=1)
        if servers.items:
            server_id = servers.items[0].id
            # Try to execute a non-existent tool
            result = client.mcp.execute_tool(
                server_id=server_id,
                tool_name="NonExistent.Tool",
                input={"test": "data"}
            )
        else:
            print("  ℹ️  No servers available for testing")
    except NotFoundError as e:
        print(f"  ❌ Tool not found: {e}")
        print(f"  Status code: {e.status_code}")
    except Exception as e:
        print(f"  ❌ Other error: {e}")
    
    # Example 4: Handle bad request errors
    print(f"\n📝 Testing bad request error handling...")
    try:
        # Get a valid server and tool first
        servers = client.mcp.list(limit=1)
        if servers.items:
            server_id = servers.items[0].id
            tools = client.mcp.get_tools(server_id)
            
            if tools:
                # Try to execute with invalid JSON structure
                result = client.mcp.execute_tool(
                    server_id=server_id,
                    tool_name=tools[0].name,
                    input="invalid_json_structure"  # Should be dict
                )
            else:
                print("  ℹ️  No tools available for testing")
        else:
            print("  ℹ️  No servers available for testing")
    except BadRequestError as e:
        print(f"  ❌ Bad request: {e}")
        print(f"  Status code: {e.status_code}")
    except Exception as e:
        print(f"  ❌ Other error: {e}")
    
    # Example 5: Handle rate limiting
    print(f"\n⏱️  Testing rate limit handling...")
    try:
        # This would trigger rate limiting in a real scenario
        for i in range(100):
            client.health.check()
    except RateLimitError as e:
        print(f"  ❌ Rate limited: {e}")
        print(f"  Status code: {e.status_code}")
        if hasattr(e, 'retry_after'):
            print(f"  Retry after: {e.retry_after} seconds")
    
    # Example 6: Handle connection errors
    print(f"\n🌐 Testing connection error handling...")
    try:
        # Use unreachable URL
        offline_client = Alter(
            api_key="test-key",
            base_url="http://unreachable-server.local"
        )
        health = offline_client.health.check()
    except APIConnectionError as e:
        print(f"  ❌ Connection failed: {e}")
    except APITimeoutError as e:
        print(f"  ❌ Request timed out: {e}")
    
    # Example 7: Comprehensive MCP error handling
    print(f"\n🛡️  Comprehensive MCP error handling...")
    try:
        # Try various MCP operations that might fail
        servers = client.mcp.list()
        
        if not servers.items:
            print("  ℹ️  No MCP servers available - deploy some servers first!")
            return
        
        server = servers.items[0]
        tools = client.mcp.get_tools(server.id)
        
        if tools:
            result = client.mcp.execute_tool(
                server_id=server.id,
                tool_name=tools[0].name,
                input={"potentially": "problematic", "data": None}
            )
            print(f"  ✅ MCP execution successful: {result.success}")
        
    except AuthenticationError:
        print("  ❌ Please check your API key")
    except NotFoundError as e:
        if "server" in str(e).lower():
            print("  ❌ MCP server not found - check server ID")
        else:
            print("  ❌ Tool not found - check the tool name")
    except BadRequestError as e:
        print(f"  ❌ Invalid MCP request: {e}")
        print("     Check your input parameters and server configuration")
    except RateLimitError:
        print("  ❌ Too many requests - please slow down")
    except APIConnectionError:
        print("  ❌ Network connection failed - check your internet")
        print("     Also verify MCP server is running and accessible")
    except APITimeoutError:
        print("  ❌ Request timed out - MCP server may be slow or overloaded")
    except APIError as e:
        print(f"  ❌ API error: {e}")
        print("     This could be an MCP server internal error")
    except AlterError as e:
        print(f"  ❌ Alter client error: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
    
    # Example 8: Raw response inspection for MCP calls
    print(f"\n🔍 Inspecting raw MCP responses...")
    try:
        # Get servers first
        servers = client.mcp.list()
        
        if servers.items:
            server_id = servers.items[0].id
            tools = client.mcp.get_tools(server_id)
            
            if tools:
                # Get raw response for debugging
                response = client.mcp.with_raw_response().execute_tool(
                    server_id=server_id,
                    tool_name=tools[0].name,
                    input={"debug": "test"}
                )
                
                print(f"  Status code: {response.status_code}")
                print(f"  Headers: {dict(response.headers)}")
                print(f"  Request ID: {response.headers.get('X-Request-ID', 'Not found')}")
                
                # Parse the actual result
                execution = response.parse()
                print(f"  Parsed result success: {execution.success}")
                print(f"  Execution ID: {execution.execution_id}")
                
            else:
                print("  ℹ️  No tools available in server")
        else:
            print("  ℹ️  No MCP servers available")
        
    except Exception as e:
        print(f"  ❌ Error with raw response: {e}")
    
    # Example 9: Retry configuration for MCP operations
    print(f"\n🔄 Testing custom retry configuration for MCP...")
    try:
        # Client with custom retry settings
        retry_client = client.with_options(
            max_retries=5,
            timeout=30.0
        )
        
        # This will retry up to 5 times with exponential backoff
        servers = retry_client.mcp.list()
        print(f"  ✅ MCP server list successful: {len(servers.items)} servers")
        
        if servers.items:
            # Test with potentially slow MCP operation
            tools = retry_client.mcp.get_tools(servers.items[0].id)
            print(f"  ✅ Tool discovery successful: {len(tools)} tools")
        
    except Exception as e:
        print(f"  ❌ Failed even with retries: {e}")
    
    # Example 10: Handling MCP server-specific errors
    print(f"\n🐳 Testing MCP server-specific error scenarios...")
    try:
        servers = client.mcp.list()
        
        for server in servers.items[:2]:  # Test first 2 servers
            try:
                print(f"  Testing server: {server.name}")
                tools = client.mcp.get_tools(server.id)
                
                if tools:
                    # Try executing with empty input (might cause server-specific errors)
                    result = client.mcp.execute_tool(
                        server_id=server.id,
                        tool_name=tools[0].name,
                        input={}
                    )
                    print(f"    ✅ {server.name}: Execution successful")
                else:
                    print(f"    ℹ️  {server.name}: No tools available")
                    
            except Exception as server_error:
                print(f"    ❌ {server.name}: Server-specific error - {server_error}")
                # Continue testing other servers
                continue
        
    except Exception as e:
        print(f"  ❌ Error in server-specific testing: {e}")

    print(f"\n💡 Error Handling Tips:")
    print("  - Always check if MCP servers are deployed and running")
    print("  - Use try-except blocks around MCP operations")
    print("  - Check server health before executing tools")
    print("  - Validate input parameters match tool schemas")
    print("  - Use raw responses for detailed debugging")
    print("  - Configure appropriate timeouts for slow MCP servers")


if __name__ == "__main__":
    main()