"""Async usage examples for the Alter Python client using MCP servers."""

import asyncio
import os
from alter import AsyncAlter

async def main():
    # Initialize the async client
    client = AsyncAlter(api_key=os.environ.get("ALTER_API_KEY"))
    
    try:
        # Concurrent operations
        print("🚀 Making concurrent API calls...")
        
        # Run multiple operations concurrently
        servers_task = client.mcp.list()
        health_task = client.health.check()
        
        servers, health = await asyncio.gather(
            servers_task, health_task
        )
        
        print(f"🔧 Available MCP servers: {len(servers)}")
        print(f"💚 Health status: {health.status}")
        
        if not servers:
            print("❌ No MCP servers found. Deploy some servers first!")
            return
        
        # Get tools from multiple servers concurrently
        print(f"\n🛠️  Getting tools from multiple servers...")
        
        tool_tasks = [
            client.mcp.get_tools(server.id) 
            for server in servers[:3]  # Get tools from first 3 servers
        ]
        
        all_server_tools = await asyncio.gather(*tool_tasks, return_exceptions=True)
        
        # Collect valid tools from all servers
        available_tools = []
        for i, tools in enumerate(all_server_tools):
            if isinstance(tools, Exception):
                print(f"  ⚠️  Failed to get tools from {servers[i].name}: {tools}")
                continue
            if tools:
                for tool in tools:
                    available_tools.append((servers[i], tool))
                print(f"  ✅ {servers[i].name}: {len(tools)} tools")
        
        if not available_tools:
            print("❌ No tools found in any server.")
            return
        
        # Execute multiple tools concurrently
        print(f"\n🚀 Executing multiple tools concurrently...")
        
        # Take first few tools for demonstration
        execution_tasks = []
        for server, tool in available_tools[:2]:  # Execute first 2 tools
            # Use generic input that works for most tools
            tool_input = {"message": f"Hello from {tool.name}!", "value": 42}
            
            task = client.mcp.execute_tool(
                server_id=server.id,
                tool_name=tool.name,
                input=tool_input
            )
            execution_tasks.append((server, tool, task))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[task for _, _, task in execution_tasks],
            return_exceptions=True
        )
        
        # Display results
        for i, result in enumerate(results):
            server, tool, _ = execution_tasks[i]
            if isinstance(result, Exception):
                print(f"  ❌ {server.name}.{tool.name}: {result}")
            else:
                print(f"  ✅ {server.name}.{tool.name}: Success")
                print(f"     Result: {str(result)[:100]}")
        
        # Demonstrate concurrent server monitoring
        print(f"\n📊 Concurrent server health checks...")
        
        # Create health check tasks (if servers support it)
        health_tasks = []
        for server in servers:
            # This is a placeholder - actual implementation depends on API
            # health_tasks.append(client.mcp.check_server_health(server.id))
            pass
        
        if health_tasks:
            health_results = await asyncio.gather(*health_tasks, return_exceptions=True)
            for i, health_result in enumerate(health_results):
                server = servers.items[i]
                if isinstance(health_result, Exception):
                    print(f"  ❌ {server.name}: Health check failed")
                else:
                    print(f"  ✅ {server.name}: Healthy")
        else:
            print("  ℹ️  Health check not available for current servers")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("  - Make sure ALTER_API_KEY environment variable is set")
        print("  - Ensure you have deployed some MCP servers")
        print("  - Check that MCP servers are running and healthy")
    
    finally:
        # Always close the async client
        await client.close()


async def context_manager_example():
    """Example using async context manager for MCP operations."""
    print("\n🔄 Using async context manager...")
    
    async with AsyncAlter(api_key=os.environ.get("ALTER_API_KEY")) as client:
        try:
            # Client is automatically closed when exiting the context
            servers = await client.mcp.list(limit=1)
            
            if not servers.items:
                print("  ❌ No MCP servers available")
                return
            
            first_server = servers.items[0]
            tools = await client.mcp.get_tools(first_server.id)
            
            if not tools:
                print(f"  ❌ No tools in server '{first_server.name}'")
                return
            
            first_tool = tools[0]
            result = await client.mcp.execute_tool(
                server_id=first_server.id,
                tool_name=first_tool.name,
                input={"message": "Hello from context manager!"}
            )
            
            print(f"  ✅ Context manager result: {result.success}")
            print(f"     Tool: {first_server.name}.{first_tool.name}")
            print(f"     Duration: {result.duration_ms}ms")
            
        except Exception as e:
            print(f"  ❌ Context manager error: {e}")


async def concurrent_server_discovery():
    """Example of concurrent server and tool discovery."""
    print("\n🔍 Concurrent server and tool discovery...")
    
    async with AsyncAlter(api_key=os.environ.get("ALTER_API_KEY")) as client:
        try:
            # Get all servers first
            all_servers = await client.mcp.list()
            
            if not all_servers.items:
                print("  ❌ No servers to discover")
                return
            
            # Discover tools from all servers concurrently
            discovery_tasks = [
                discover_server_capabilities(client, server)
                for server in all_servers.items
            ]
            
            capabilities = await asyncio.gather(*discovery_tasks, return_exceptions=True)
            
            # Display discovery results
            for i, capability in enumerate(capabilities):
                server = all_servers.items[i]
                if isinstance(capability, Exception):
                    print(f"  ❌ {server.name}: Discovery failed - {capability}")
                else:
                    tool_count, sample_tool = capability
                    print(f"  ✅ {server.name}: {tool_count} tools (e.g., {sample_tool})")
                    
        except Exception as e:
            print(f"  ❌ Discovery error: {e}")


async def discover_server_capabilities(client, server):
    """Helper function to discover what a server can do."""
    try:
        tools = await client.mcp.get_tools(server.id)
        if tools:
            return len(tools), tools[0].name
        else:
            return 0, "No tools"
    except Exception as e:
        raise Exception(f"Failed to get tools: {e}")


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(context_manager_example())  
    asyncio.run(concurrent_server_discovery())