from blender_mcp.server import main as server_main
import sys

def main():
    """Entry point for the blender-mcp package.
    
    Runs the MCP server that connects Blender to AI assistants via
    the Model Context Protocol.

    Note: Make sure Blender is open and the blender-mcp addon is enabled
    before starting this server, otherwise connections will fail.
    """
    # Print a startup message so it's clear the server is launching
    print("Starting Blender MCP server...", file=sys.stderr)
    print("Tip: Ensure Blender is running with the MCP addon enabled.", file=sys.stderr)
    server_main()

if __name__ == "__main__":
    main()
