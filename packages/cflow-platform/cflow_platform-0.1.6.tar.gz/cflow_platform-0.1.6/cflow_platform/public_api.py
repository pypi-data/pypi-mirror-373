"""Thin wrapper re-exporting the CFlow public API from the monorepo path.

This allows early adoption of the import path `cflow_platform.public_api` while
the code still lives under `.cerebraflow/` during Phase 1.
"""

from typing import Any, Callable, Dict
from pathlib import Path
import importlib.util


def _load_monorepo_public_api():
    base = Path(__file__).resolve().parents[2]
    api_path = base / ".cerebraflow" / "core" / "mcp" / "core" / "public_api.py"
    spec = importlib.util.spec_from_file_location("cflow_public_api", str(api_path))
    if spec is None or spec.loader is None:
        raise ImportError("Cannot locate monorepo public_api.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


_api = _load_monorepo_public_api()


def get_stdio_server() -> Callable[[], Any]:
    return _api.get_stdio_server()


def get_direct_client_executor() -> Callable[..., Any]:
    return _api.get_direct_client_executor()


def safe_get_version_info() -> Dict[str, Any]:
    return _api.safe_get_version_info()


