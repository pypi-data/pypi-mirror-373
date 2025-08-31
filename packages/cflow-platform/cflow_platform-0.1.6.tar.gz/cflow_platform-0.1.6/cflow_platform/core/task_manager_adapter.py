from __future__ import annotations

from typing import Any, Dict, List, Optional
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec


def _load_monorepo_task_manager() -> Any:
    """Load TaskManager class from monorepo by file path to avoid import loops."""
    # Repo root: .../Cerebral
    repo_root = Path(__file__).resolve().parents[4]
    tm_path = repo_root / ".cerebraflow" / "core" / "mcp" / "core" / "task_manager.py"
    spec = spec_from_file_location("monorepo_task_manager", str(tm_path))
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load monorepo TaskManager module")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return getattr(mod, "TaskManager")


class TaskManagerAdapter:
    """Adapter exposing simple methods used by package handlers, backed by monorepo TaskManager."""

    def __init__(self, tenant_id: Optional[str] = None):
        TaskManager = _load_monorepo_task_manager()
        self._manager = TaskManager(tenant_id=tenant_id or "00000000-0000-0000-0000-000000000100")

    async def get_task_stats(self) -> Dict[str, int]:
        return await self._manager.get_task_stats()

    async def list_tasks(self, status: Optional[str] = None, include_subtasks: bool = False) -> List[Dict[str, Any]]:
        # Default to pending if no status requested
        status_to_use = status or "pending"
        return await self._manager.get_tasks_by_status(status_to_use)

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return await self._manager.get_task_by_id(task_id)

    async def next_task(self) -> Optional[Dict[str, Any]]:
        pending = await self._manager.get_tasks_by_status("pending")
        return pending[0] if pending else None

    async def update_task_status(self, task_id: str, status: str) -> bool:
        return await self._manager.update_task_status(task_id, status)

    async def add_task(self, title: str, description: str, priority: str = "medium") -> str:
        return await self._manager.add_task(title, description, priority)

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        # Monorepo manager currently logs update and returns True
        return await self._manager.update_task(task_id, updates)

    async def delete_task(self, task_id: str) -> bool:
        return await self._manager.delete_task(task_id)


