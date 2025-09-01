from .server import mcp

def main() -> None:
    # Starts the server over STDIO (what MCP clients expect)
    print("Starting Demo MCP Server (stdio)… waiting for a client. Press Ctrl+C to exit.")
    mcp.run()
