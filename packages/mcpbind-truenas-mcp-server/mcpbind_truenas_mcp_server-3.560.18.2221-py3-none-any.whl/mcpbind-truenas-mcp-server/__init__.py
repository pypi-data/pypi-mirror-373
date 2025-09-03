"""
mcpbind-truenas-mcp-server - MCP Server Package for truenas-mcp-server
"""

__version__ = "3.560.18.2221"

def main():
    """Main entry point for the MCP server."""
    print("MCP Server truenas-mcp-server starting...")
    print(f"Version: {build_version}")
    return 0

if __name__ == "__main__":
    main()
