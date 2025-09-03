"""
mcpbind-cockroachdb-mcp-server - MCP Server Package for cockroachdb-mcp-server
"""

__version__ = "3.440.58.2964"

def main():
    """Main entry point for the MCP server."""
    print("MCP Server cockroachdb-mcp-server starting...")
    print(f"Version: {build_version}")
    return 0

if __name__ == "__main__":
    main()
