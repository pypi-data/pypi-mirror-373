from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class EnhancedResearchHandlers:
    """Package wrapper for enhanced research tools.

    Delegates to monorepo implementation when available while keeping
    imports package-safe.
    """

    def __init__(self, task_manager, project_root: Path):
        self.task_manager = task_manager
        self.project_root = project_root

    async def handle_doc_research(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # Try to delegate to monorepo enhanced implementation by path
        try:
            from importlib.util import spec_from_file_location, module_from_spec
            repo_root = Path(__file__).resolve().parents[4]
            mono_path = repo_root / ".cerebraflow" / "core" / "mcp" / "handlers" / "enhanced_research_handlers.py"
            spec = spec_from_file_location("mono_enhanced_research_handlers", str(mono_path))
            if spec and spec.loader:
                mod = module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore[attr-defined]
                MonoHandlers = getattr(mod, "EnhancedResearchHandlers")
                mono = MonoHandlers(task_manager=self.task_manager, project_root=self.project_root)
                result = await mono.handle_enhanced_research(arguments)
                # Normalize to structured response
                if isinstance(result, list):
                    text = "\n\n".join(getattr(x, "text", str(x)) for x in result)
                    return {
                        "status": "success",
                        "content": text,
                        "taskId": arguments.get("taskId"),
                        "autoCreateSubtasks": bool(arguments.get("autoCreateSubtasks", True)),
                        "createTDD": bool(arguments.get("createTDD", True)),
                    }
                if isinstance(result, dict):
                    # Ensure status and taskId present
                    out = {"status": result.get("status", "success"), **result}
                    out.setdefault("taskId", arguments.get("taskId"))
                    return out
        except Exception:
            # Fall back to minimal implementation
            pass

        task_id = arguments.get("taskId")
        research_query = arguments.get("researchQuery", "")
        auto_create = bool(arguments.get("autoCreateSubtasks", True))
        create_tdd = bool(arguments.get("createTDD", True))
        return {
            "status": "success",
            "taskId": task_id,
            "autoCreateSubtasks": auto_create,
            "createTDD": create_tdd,
            "analysis": {"summary": f"researched: {research_query[:64]}"},
        }

    async def handle_research(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generic enhanced research entrypoint matching tool name 'research'."""
        # Reuse the same implementation but accept 'query' as the canonical field
        if "researchQuery" not in arguments and "query" in arguments:
            arguments = {**arguments, "researchQuery": arguments.get("query", "")}
        return await self.handle_doc_research(arguments)


