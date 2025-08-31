from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path


class TaskModificationHandlers:
    def __init__(self, task_manager):
        self.task_manager = task_manager

    async def handle_task_add(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        title = arguments.get("title", "Untitled")
        description = arguments.get("description", "")
        priority = arguments.get("priority", "medium")
        task_id = await self.task_manager.add_task(title, description, priority)
        return {"status": "success", "taskId": task_id}

    async def handle_task_update(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        updates = arguments.get("updates", {})
        ok = await self.task_manager.update_task(task_id, updates)
        return {"status": "success" if ok else "error", "taskId": task_id}

    async def handle_task_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        status = arguments.get("status", "pending")
        ok = await self.task_manager.update_task_status(task_id, status)
        return {"status": "success" if ok else "error", "taskId": task_id, "newStatus": status}

    async def handle_task_sub_add(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Create a task and record parent reference in details for hierarchical linkage
        parent_id = arguments.get("parentId")
        title = arguments.get("title", "Untitled")
        description = arguments.get("description", "")
        task_id = await self.task_manager.add_task(title, description, "medium")
        await self.task_manager.update_task(task_id, {"parentId": parent_id})
        return {"status": "success", "taskId": task_id, "parentId": parent_id}

    async def handle_task_sub_upd(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        subtask_id = arguments.get("taskId")
        notes = arguments.get("notes", "")
        ok = await self.task_manager.update_task(subtask_id, {"notes": notes})
        return {"status": "success" if ok else "error", "taskId": subtask_id}

    async def handle_task_multi(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        from_id = arguments.get("fromId")
        updates = arguments.get("updates", {})
        # Apply updates to the starting task; batch application can be extended later
        ok = await self.task_manager.update_task(from_id, updates)
        return {"status": "success" if ok else "error", "updated": 1}

    async def handle_task_remove(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        ok = await self.task_manager.delete_task(task_id)
        return {"status": "success" if ok else "error", "taskId": task_id}


