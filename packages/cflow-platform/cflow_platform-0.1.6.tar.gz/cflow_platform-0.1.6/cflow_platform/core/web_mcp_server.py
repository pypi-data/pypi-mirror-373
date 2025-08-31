from __future__ import annotations

from typing import Any, Dict


def get_web_mcp_server_binding() -> Dict[str, Any]:
    """Return a simple descriptor for WebMCP server bindings.

    The monorepo shim can import this and register routes accordingly.
    """
    return {
        "transport": "websocket",
        "path": "/mcp",
        "protocol": "jsonrpc",
    }


