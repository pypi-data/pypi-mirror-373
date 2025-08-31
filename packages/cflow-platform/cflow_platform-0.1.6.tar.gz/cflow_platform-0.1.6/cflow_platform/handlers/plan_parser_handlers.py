from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict


class PlanParserHandlers:
    """Package wrapper for atomic plan parsing tools.

    Delegates to the monorepo AtomicPlanParser via import-by-path to avoid
    tight coupling during the split.
    """

    def __init__(self):
        self._parser = None

    def _get_parser(self):
        if self._parser:
            return self._parser
        # Load monorepo parser by path
        from importlib.util import spec_from_file_location, module_from_spec
        repo_root = Path(__file__).resolve().parents[4]
        parser_path = repo_root / ".cerebraflow" / "framework" / "atomic_plan_parser.py"
        spec = spec_from_file_location("monorepo_atomic_plan_parser", str(parser_path))
        if spec is None or spec.loader is None:
            raise ImportError("Unable to load AtomicPlanParser module")
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[attr-defined]
        self._parser = getattr(mod, "AtomicPlanParser")(tenant_id=os.getenv('CEREBRAFLOW_TENANT_ID', '00000000-0000-0000-0000-000000000100'))
        return self._parser

    async def parse_atomic_plan(self, **kwargs: Any) -> Dict[str, Any]:
        plan_file = kwargs.get("plan_file")
        dry_run = bool(kwargs.get("dry_run", False))
        tenant_id = kwargs.get("tenant_id")
        if not plan_file:
            return {"success": False, "error": "plan_file parameter is required"}
        file_path = Path(plan_file)
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
        if not file_path.exists():
            return {"success": False, "error": f"Plan file not found: {file_path}"}
        parser = self._get_parser()
        if tenant_id:
            parser.tenant_id = tenant_id
        if dry_run:
            plan_data = parser.parse_atomic_plan(str(file_path))
            return {
                "success": True,
                "operation": "parse_only",
                "tasks_parsed": len(plan_data.get("tasks", [])),
                "plan_info": plan_data.get("plan_info", {}),
                "statistics": plan_data.get("statistics", {}),
            }
        result = parser.parse_and_store(str(file_path))
        return {
            "success": result.get("success", False),
            "operation": "parse_and_store",
            "tasks_parsed": result.get("tasks_parsed", 0),
            "tasks_stored": result.get("tasks_stored", 0),
            "plan_info": result.get("plan_info", {}),
            "statistics": result.get("statistics", {}),
            "message": result.get("message", ""),
        }

    async def list_available_plans(self, **kwargs: Any) -> Dict[str, Any]:
        search_path = kwargs.get("search_path", "docs/plans")
        base_path = Path(search_path)
        if not base_path.is_absolute():
            base_path = Path.cwd() / base_path
        plans = []
        if base_path.exists():
            for md in base_path.glob("**/*.md"):
                plans.append({
                    "file": str(md.relative_to(Path.cwd())),
                    "absolute_path": str(md),
                    "size_kb": md.stat().st_size / 1024,
                    "modified": md.stat().st_mtime,
                })
        return {"success": True, "plans_found": len(plans), "search_path": str(base_path), "plans": sorted(plans, key=lambda x: x["modified"], reverse=True)}

    async def validate_plan_format(self, **kwargs: Any) -> Dict[str, Any]:
        # Delegate to monorepo AtomicPlanParser for validation when available
        plan_file = kwargs.get("plan_file")
        if not plan_file:
            return {"success": False, "error": "plan_file parameter is required"}
        try:
            parser = self._get_parser()
            file_path = Path(plan_file)
            if not file_path.is_absolute():
                file_path = Path.cwd() / file_path
            if not file_path.exists():
                return {"success": False, "error": f"Plan file not found: {file_path}"}
            plan_data = parser.parse_atomic_plan(str(file_path))
            has_tasks = bool(plan_data.get("tasks"))
            return {"success": True, "file_valid": True, "has_tasks": has_tasks, "plan_info": plan_data.get("plan_info", {})}
        except Exception as e:
            return {"success": False, "error": f"Plan validation failed: {e}"}


