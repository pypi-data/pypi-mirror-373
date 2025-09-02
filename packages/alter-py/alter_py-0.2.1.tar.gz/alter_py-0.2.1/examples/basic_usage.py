"""Basic usage examples for the Alter Python client using MCP servers."""

import os
from alter import Alter

def main():
    # Initialize the client
    client = Alter(api_key=os.environ.get("ALTER_API_KEY"))
    
    try:
        # List available MCP servers
        print("\n🔧 Available MCP servers:")
        servers = client.mcp.list()
        if not servers:
            print("  No MCP servers found. Deploy some servers first!")
            return
            
        for server in servers[:5]:  # Show first 5 servers
            print(f"  - {server.name}: {server.status}")
        
        # Pick the first server and list its tools
        first_server = servers[0]
        print(f"\n🛠️  Tools in '{first_server.name}' server:")
        tools = client.mcp.get_tools(first_server.id)
        
        if not tools:
            print("  No tools found in this server.")
            return
            
        for tool in tools[:3]:  # Show first 3 tools
            print(f"  - {tool.name}: {tool.description or 'No description'}")
        
        # Execute a tool from the first server
        first_tool = tools[0]
        print(f"\n🚀 Executing '{first_tool.name}' tool...")
        
        # Example input - adjust based on your tool's requirements
        tool_input = {"message": "Hello from Alter Python SDK!"}
        
        result = client.mcp.execute_tool(
            server_id=first_server.id,
            tool_name=first_tool.name,
            input=tool_input
        )
        
        print(f"  🎯 Result: {result}")
        # List all MCP servers with their status
        print(f"\n🌐 All MCP servers:")
        all_servers = client.mcp.list()
        for server in all_servers:
            server_type = "🐳 Platform" if server.server_type == "platform" else "🔗 External"
            print(f"  {server_type} - {server.name}: {server.status}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("  - Make sure ALTER_API_KEY environment variable is set")
        print("  - Ensure you have deployed some MCP servers in the dashboard")
        print("  - Check that the MCP server is running and healthy")


if __name__ == "__main__":
    main()