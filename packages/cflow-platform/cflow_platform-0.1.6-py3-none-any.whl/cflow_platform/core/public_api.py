"""CFlow Platform Core Public API (Phase 2 scaffold)

Provides stable import points for stdio server, direct client executor, and
version info. During the split, these delegate to local cflow_platform modules
if present, otherwise fall back to the monorepo bindings.
"""

from typing import Any, Callable, Dict
import importlib


def get_stdio_server() -> Callable[[], Any]:
    try:
        from cflow_platform.core.server.stdio import stdio_server  # type: ignore
        return stdio_server
    except Exception:
        # Fallback to monorepo wrapper
        from cflow_platform.public_api import get_stdio_server as _m
        return _m()


def get_direct_client_executor() -> Callable[..., Any]:
    try:
        from cflow_platform.core.direct_client import execute_mcp_tool  # type: ignore
        return execute_mcp_tool
    except Exception:
        from cflow_platform.public_api import get_direct_client_executor as _m
        return _m()


def safe_get_version_info() -> Dict[str, Any]:
    try:
        from cflow_platform.core.tool_registry import ToolRegistry  # type: ignore
        return ToolRegistry.get_version_info()
    except Exception:
        from cflow_platform.public_api import safe_get_version_info as _m
        return _m()


