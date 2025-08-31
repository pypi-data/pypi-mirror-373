from pathlib import Path
from typing import Any, Dict
from datetime import datetime


class RAGHandlers:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    async def handle_doc_generate(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        content = arguments.get("content", f"# TDD for Task {task_id}\n\nGenerated at {datetime.now().isoformat()}\n")
        path = self._write_tdd(task_id, content) if task_id else None
        return {"status": "success", "taskId": task_id, "doc": "generated", "path": path}

    async def handle_doc_quality(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        tdd_dir = self.project_root / ".cerebraflow" / "docs" / "tdds"
        tdd_files = list(tdd_dir.glob(f"TDD_{task_id}_*.md")) if task_id else []
        has_tdd = bool(tdd_files)
        return {"status": "success", "taskId": task_id, "score": 1.0 if has_tdd else 0.5}

    async def handle_doc_refs(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        refs = ["docs/plans/platform-reboot/PLATFORM_REBOOT_MASTER_PLAN.md"]
        tdd_dir = self.project_root / ".cerebraflow" / "docs" / "tdds"
        if task_id:
            refs.extend([str(p) for p in tdd_dir.glob(f"TDD_{task_id}_*.md")])
        return {"status": "success", "taskId": task_id, "refs": refs}

    async def handle_doc_research(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        query = arguments.get("query", "")
        return {"status": "success", "taskId": task_id, "query": query, "notes": "ok"}

    async def handle_doc_comply(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        task_id = arguments.get("taskId")
        framework = arguments.get("framework", "SOC2")
        return {"status": "success", "taskId": task_id, "framework": framework}

    def _write_tdd(self, task_id: str, content: str) -> str:
        tdd_dir = self.project_root / ".cerebraflow" / "docs" / "tdds"
        tdd_dir.mkdir(parents=True, exist_ok=True)
        path = tdd_dir / f"TDD_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        path.write_text(content, encoding="utf-8")
        return str(path)


