from blender_mcp.server import main as server_main
import sys

DEFAULT_PORT = 9876

def main():
    """Entry point for the blender-mcp package.
    
    Runs the MCP server that connects Blender to AI assistants via
    the Model Context Protocol.

    Note: Make sure Blender is open and the blender-mcp addon is enabled
    before starting this server, otherwise connections will fail.

    The addon can be found in the Blender preferences under Add-ons.
    Default connection port is 9876.

    Troubleshooting:
        - If the server fails to connect, try restarting the addon in Blender.
        - On Windows, firewall rules may block the connection on port 9876.
        - On macOS, you may need to allow the connection in System Settings > Privacy & Security.
        - On Linux, check that no other process is using port 9876 with: lsof -i :9876
    """
    # Print a startup message so it's clear the server is launching
    print("Starting Blender MCP server...", file=sys.stderr)
    print(f"Tip: Ensure Blender is running with the MCP addon enabled on port {DEFAULT_PORT}.", file=sys.stderr)
    print("Tip: Check Edit > Preferences > Add-ons and search for 'Blender MCP'.", file=sys.stderr)
    # Personal note: I also find it helpful to open Blender's system console
    # (Window > Toggle System Console) to see addon-side logs during debugging.
    # Personal note: On my machine I sometimes run two Blender instances, so I
    # occasionally change DEFAULT_PORT to 9877 for the second one to avoid conflicts.
    server_main()

if __name__ == "__main__":
    main()
