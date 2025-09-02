"""Comprehensive examples: Using MCP servers through the Alter SDK."""

import asyncio
import os
from typing import List, Dict, Any

from alter import Alter, AsyncAlter
from alter import (
    AlterError,
    APIError,
    AuthenticationError,
    NotFoundError,
    BadRequestError,
    APIConnectionError
)

try:
    from langchain_alter import AlterToolkit
    from langchain.agents import create_react_agent
    from langchain.llms import OpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("⚠️  LangChain not installed. Install with: pip install langchain-alter")
    LANGCHAIN_AVAILABLE = False


def example_1_basic_mcp_usage():
    """Example 1: Basic MCP server discovery and tool listing."""
    print("\n=== Example 1: Basic MCP Usage ===")
    
    try:
        # Initialize Alter client
        client = Alter()
        
        # List all accessible MCP servers
        print("📋 Available MCP servers:")
        servers = client.mcp.list()
        
        if not servers:
            print("  No MCP servers found. Make sure you have deployed or registered some MCP servers.")
            return
        
        # Show server details by type
        external_servers = [s for s in servers if s.server_type == "external"]
        platform_servers = [s for s in servers if s.server_type == "platform"]
        
        if external_servers:
            print("\n🌐 External MCP Servers (User-provided):")
            for server in external_servers:
                print(f"  - {server.name}: {server.status} (ID: {server.id})")
        
        if platform_servers:
            print("\n🐳 Platform MCP Servers (Docker containers):")
            for server in platform_servers:
                print(f"  - {server.name}: {server.deployment_status} (ID: {server.id})")
        
        # Get tools from first available server
        first_server = servers[0]
        print(f"\n🔧 Tools from '{first_server.name}':")
        
        try:
            tools = client.mcp.get_tools(first_server.id)
            if tools:
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                    # Show first few parameters
                    if hasattr(tool, 'parameters') and tool.parameters:
                        params = list(tool.parameters.keys())[:3]
                        if params:
                            print(f"    Parameters: {', '.join(params)}{'...' if len(tool.parameters) > 3 else ''}")
            else:
                print("  No tools found in this server.")
                
        except NotFoundError:
            print(f"  ❌ Server '{first_server.name}' not found or not accessible")
        except APIError as e:
            print(f"  ❌ Error getting tools: {e}")
            
    except AuthenticationError:
        print("❌ Authentication failed. Please check your API key.")
    except APIConnectionError:
        print("❌ Cannot connect to Alter API. Check your internet connection.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def example_2_tool_execution_with_error_handling():
    """Example 2: Execute MCP tools with comprehensive error handling."""
    print("\n=== Example 2: Tool Execution with Error Handling ===")
    
    try:
        client = Alter()
        servers = client.mcp.list()
        
        if not servers:
            print("No servers available for tool execution.")
            return
        
        # Find a server with tools
        server_with_tools = None
        available_tools = []
        
        for server in servers:
            try:
                tools = client.mcp.get_tools(server.id)
                if tools:
                    server_with_tools = server
                    available_tools = tools
                    break
            except Exception as e:
                print(f"⚠️  Could not get tools from {server.name}: {e}")
                continue
        
        if not server_with_tools:
            print("No servers with available tools found.")
            return
        
        print(f"🚀 Executing tool from '{server_with_tools.name}'...")
        
        # Try to execute the first available tool
        first_tool = available_tools[0]
        print(f"Tool: {first_tool.name}")
        
        # Example with simple parameters (modify based on actual tool)
        sample_input = {"message": "Hello from Alter SDK!"}
        
        try:
            result = client.mcp.execute_tool(
                server_id=server_with_tools.id,
                tool_name=first_tool.name,
                input=sample_input
            )
            print(f"✅ Execution successful!")
            print(f"Result: {result}")
            
        except BadRequestError as e:
            print(f"❌ Invalid parameters for tool '{first_tool.name}': {e}")
            print("Try adjusting the input parameters based on the tool's requirements.")
        except NotFoundError:
            print(f"❌ Tool '{first_tool.name}' not found on server '{server_with_tools.name}'")
        except APIError as e:
            print(f"❌ API error during execution: {e}")
            
    except Exception as e:
        print(f"❌ Unexpected error in tool execution: {e}")


async def example_3_async_mcp_operations():
    """Example 3: Async MCP operations for better performance."""
    print("\n=== Example 3: Async MCP Operations ===")
    
    async with AsyncAlter() as client:
        try:
            # Fetch servers and health check concurrently
            print("🔄 Making concurrent API calls...")
            
            servers_task = client.mcp.list()
            health_task = client.health.check()
            
            servers, health = await asyncio.gather(
                servers_task, health_task,
                return_exceptions=True
            )
            
            if isinstance(servers, Exception):
                print(f"❌ Error fetching servers: {servers}")
                return
                
            if isinstance(health, Exception):
                print(f"⚠️  Health check failed: {health}")
            else:
                print(f"💚 API Health: {health.status}")
            
            print(f"📋 Found {len(servers)} MCP servers")
            
            if not servers:
                return
            
            # Get tools from multiple servers concurrently
            print("🔧 Getting tools from all servers concurrently...")
            
            tool_tasks = [
                client.mcp.get_tools(server.id) 
                for server in servers[:3]  # Limit to first 3 servers
            ]
            
            tools_results = await asyncio.gather(
                *tool_tasks, 
                return_exceptions=True
            )
            
            total_tools = 0
            for i, (server, tools_result) in enumerate(zip(servers[:3], tools_results)):
                if isinstance(tools_result, Exception):
                    print(f"  ❌ {server.name}: Error getting tools - {tools_result}")
                else:
                    print(f"  ✅ {server.name}: {len(tools_result)} tools")
                    total_tools += len(tools_result)
            
            print(f"\n📊 Total tools across all servers: {total_tools}")
            
        except AuthenticationError:
            print("❌ Authentication failed for async operations")
        except Exception as e:
            print(f"❌ Unexpected error in async operations: {e}")


def example_4_langchain_integration():
    """Example 4: LangChain integration with MCP tools."""
    print("\n=== Example 4: LangChain Integration ===")
    
    if not LANGCHAIN_AVAILABLE:
        print("Skipping LangChain example - package not installed")
        return
    
    try:
        # Initialize Alter client and toolkit
        client = Alter()
        toolkit = AlterToolkit(client=client)
        
        print("🔗 Getting all MCP tools as LangChain tools...")
        all_tools = toolkit.get_tools()
        
        if not all_tools:
            print("No MCP tools available for LangChain integration.")
            return
        
        print(f"✅ Found {len(all_tools)} tools total across all servers")
        
        # Show available tools
        print("\n📋 Available LangChain tools:")
        for tool in all_tools[:5]:  # Show first 5
            print(f"  - {tool.name}: {tool.description}")
        
        if len(all_tools) > 5:
            print(f"  ... and {len(all_tools) - 5} more tools")
        
        # Example: Create a simple agent (requires OpenAI API key)
        if os.environ.get("OPENAI_API_KEY"):
            print("\n🤖 Creating LangChain agent...")
            
            try:
                llm = OpenAI(temperature=0)
                
                # Create a simple prompt
                from langchain.schema import SystemMessage
                prompt = "You are a helpful assistant with access to MCP tools."
                
                # You could create an agent here, but we'll just show the setup
                print(f"✅ Agent ready with {len(all_tools)} tools")
                print("Note: Actual agent execution requires a specific use case and prompt.")
                
            except Exception as e:
                print(f"❌ Error creating agent: {e}")
        else:
            print("\n💡 Set OPENAI_API_KEY environment variable to test agent creation")
            
    except Exception as e:
        print(f"❌ Error in LangChain integration: {e}")


def example_5_server_type_differences():
    """Example 5: Understanding different MCP server types."""
    print("\n=== Example 5: Server Type Differences ===")
    
    try:
        client = Alter()
        servers = client.mcp.list()
        
        if not servers:
            print("No servers available to analyze.")
            return
        
        print("🔍 Analyzing server types and their characteristics:")
        
        for server in servers:
            print(f"\n📡 {server.name} (ID: {server.id})")
            print(f"   Type: {server.server_type}")
            print(f"   Status: {server.status}")
            
            if server.server_type == "external":
                print("   ℹ️  External server - User-provided endpoint")
                print("   - Managed outside of Alter platform")
                print("   - Direct connection to user's infrastructure")
                print("   - Status reflects external server health")
                
            elif server.server_type == "platform":
                print("   ℹ️  Platform server - Docker container")
                print(f"   - Deployment status: {server.deployment_status}")
                print("   - Managed by Alter platform")
                print("   - Can be started/stopped via dashboard")
            
            # Try to get tools to show capabilities
            try:
                tools = client.mcp.get_tools(server.id)
                print(f"   🔧 Available tools: {len(tools)}")
                
                if tools:
                    # Show tool categories/types
                    tool_names = [t.name for t in tools[:3]]
                    print(f"   Examples: {', '.join(tool_names)}{'...' if len(tools) > 3 else ''}")
                    
            except Exception as e:
                print(f"   ❌ Could not fetch tools: {e}")
    
    except Exception as e:
        print(f"❌ Error analyzing server types: {e}")


def main():
    """Run all MCP usage examples."""
    print("🚀 Alter SDK - MCP Integration Examples")
    print("=" * 50)
    
    # Check API key
    if not os.environ.get("ALTER_API_KEY"):
        print("⚠️  ALTER_API_KEY environment variable not set.")
        print("   Set it with: export ALTER_API_KEY='your-api-key'")
        print("   Some examples may fail without authentication.\n")
    
    # Run synchronous examples
    example_1_basic_mcp_usage()
    example_2_tool_execution_with_error_handling()
    example_4_langchain_integration()
    example_5_server_type_differences()
    
    # Run async example
    print("\n🔄 Running async example...")
    asyncio.run(example_3_async_mcp_operations())
    
    print("\n✅ All examples completed!")
    print("\n💡 Next steps:")
    print("   1. Deploy or register MCP servers via the dashboard")
    print("   2. Try executing tools with your specific parameters")
    print("   3. Integrate with LangChain agents for complex workflows")


if __name__ == "__main__":
    main()