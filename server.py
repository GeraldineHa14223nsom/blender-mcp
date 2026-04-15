"""MCP server implementation for Blender integration.

This module defines the MCP (Model Context Protocol) server that exposes
Blender operations as tools callable by AI assistants.
"""

import json
import socket
import threading
from typing import Any

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9876
BUFFER_SIZE = 4096


class BlenderMCPHandler:
    """Handles incoming MCP requests and dispatches them to Blender."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self._socket: socket.socket | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Start the MCP handler server in a background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()
        print(f"[BlenderMCP] Handler listening on {self.host}:{self.port}")

    def stop(self) -> None:
        """Stop the MCP handler server."""
        self._running = False
        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        print("[BlenderMCP] Handler stopped.")

    def _serve(self) -> None:
        """Main server loop — accept connections and handle requests."""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self.host, self.port))
        self._socket.listen(5)
        self._socket.settimeout(1.0)

        while self._running:
            try:
                conn, addr = self._socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(conn, addr),
                    daemon=True,
                )
                client_thread.start()
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle_client(self, conn: socket.socket, addr: tuple) -> None:
        """Read a JSON request from a client and return a JSON response."""
        try:
            data = b""
            while True:
                chunk = conn.recv(BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
                if data.endswith(b"\n"):
                    break

            if not data:
                return

            request = json.loads(data.decode("utf-8").strip())
            response = self._dispatch(request)
            payload = (json.dumps(response) + "\n").encode("utf-8")
            conn.sendall(payload)
        except (json.JSONDecodeError, OSError) as exc:
            error_payload = (
                json.dumps({"error": str(exc)}) + "\n"
            ).encode("utf-8")
            try:
                conn.sendall(error_payload)
            except OSError:
                pass
        finally:
            conn.close()

    def _dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        """Route an incoming request to the appropriate handler method."""
        tool = request.get("tool", "")
        params = request.get("params", {})

        handler = getattr(self, f"_tool_{tool}", None)
        if handler is None:
            return {"error": f"Unknown tool: '{tool}'"}

        try:
            result = handler(**params)
            return {"result": result}
        except TypeError as exc:
            return {"error": f"Invalid parameters for '{tool}': {exc}"}
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Built-in tools
    # ------------------------------------------------------------------

    def _tool_ping(self) -> str:
        """Health-check tool — returns 'pong'."""
        return "pong"

    def _tool_get_scene_info(self) -> dict[str, Any]:
        """Return basic information about the current Blender scene."""
        try:
            import bpy  # type: ignore[import]

            scene = bpy.context.scene
            objects = [
                {"name": obj.name, "type": obj.type}
                for obj in scene.objects
            ]
            return {
                "scene_name": scene.name,
                "frame_current": scene.frame_current,
                "object_count": len(objects),
                "objects": objects,
            }
        except ImportError:
            return {"error": "bpy not available outside Blender"}
