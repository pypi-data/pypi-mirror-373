import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


logger = logging.getLogger(__name__)


class SystemHandlers:
    def __init__(self, task_manager, project_root: Path):
        self.task_manager = task_manager
        self.project_root = project_root

    async def handle_test_connection(self, arguments: Dict[str, Any]) -> List[Dict[str, str]]:
        try:
            connection_info = {
                "status": "connected",
                "server": "CFlow-stdio",
                "timestamp": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "python_version": sys.version,
                "working_directory": str(Path.cwd()),
            }
            try:
                stats = await self.task_manager.get_task_stats()
                connection_info["task_system"] = {
                    "status": "operational",
                    "total_tasks": stats.get("total", 0),
                }
            except Exception as e:
                connection_info["task_system"] = {"status": "error", "error": str(e)}

            return [{"type": "text", "text": json_dump(connection_info)}]
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return [{"type": "text", "text": f"error: {e}"}]

    async def handle_get_stats(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        stats = await _safe_call(self.task_manager.get_task_stats)
        return {"status": "success", "stats": stats or {}}

    async def handle_debug_environment(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        info = {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "cwd": str(Path.cwd()),
            "timestamp": datetime.now().isoformat(),
        }
        return {"status": "success", "environment": info}

    async def handle_version_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        from cflow_platform.core.tool_registry import ToolRegistry  # type: ignore
        return {"status": "success", "version": ToolRegistry.get_version_info()}


def json_dump(data: Dict[str, Any]) -> str:
    import json
    return json.dumps(data)


async def _safe_call(fn):
    try:
        return await fn()
    except Exception:
        return None


