"""CFlow Python SDK (Phase 1): thin proxy to public API/direct client.

Provides a stable client surface that will remain compatible after the
repo split. Internally bridges to the monorepo's public_api module.
"""

from __future__ import annotations

from typing import Any, Dict
from pathlib import Path
import importlib.util


def _load_public_api():
    try:
        # Package import path
        from . import public_api as api  # type: ignore
        return api
    except Exception:
        # Fallback to path import
        base = Path(__file__).resolve().parents[0]
        api_path = base / "public_api.py"
        spec = importlib.util.spec_from_file_location("cflow_platform_public_api", str(api_path))
        if spec is None or spec.loader is None:
            raise ImportError("Cannot locate cflow_platform.public_api")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        return module


_public_api = _load_public_api()


class CFlowClient:
    """Simple client to execute MCP tools via the direct client executor."""

    def __init__(self) -> None:
        self._exec = _public_api.get_direct_client_executor()

    async def execute_tool(self, tool_name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute an MCP tool by name.

        Returns a dict with at least keys: status, and optionally result/message.
        """
        return await self._exec(tool_name, **kwargs)


