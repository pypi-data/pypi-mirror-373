from pathlib import Path
from typing import Any, Dict, List


class TaskHandlers:
    def __init__(self, task_manager, project_root: Path):
        self.task_manager = task_manager
        self.project_root = project_root

    async def handle_list_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        status = arguments.get("status")
        include_subtasks = bool(arguments.get("includeSubtasks", False))
        items = await self.task_manager.list_tasks(status=status, include_subtasks=include_subtasks)
        return {"status": "success", "tasks": items}

    async def handle_get_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        item = await self.task_manager.get_task(task_id)
        return {"status": "success", "task": item}

    async def handle_next_task(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        item = await self.task_manager.next_task()
        return {"status": "success", "task": item}


