from __future__ import annotations

from typing import Any, Dict, List


class ToolRegistry:
    """Package-side MCP tool registry definitions for monorepo consumption.

    Returns plain dict tool specs so the monorepo can construct mcp.types.Tool
    without requiring this package to import MCP libraries.
    """

    @staticmethod
    def get_tools_for_mcp() -> List[Dict[str, Any]]:
        tools: List[Dict[str, Any]] = []

        def tool(name: str, description: str, schema: Dict[str, Any] | None = None) -> Dict[str, Any]:
            return {
                "name": name,
                "description": description,
                "inputSchema": schema or {"type": "object", "properties": {}, "required": []},
            }

        # System
        tools += [
            tool("sys_test", "Test stdio server connection"),
            tool("sys_stats", "Project statistics overview"),
            tool("sys_debug", "Debug environment"),
            tool("sys_version", "MCP version info"),
        ]

        # Tasks (read)
        tools += [
            tool("task_list", "List/filter tasks", {"type": "object", "properties": {"status": {"type": "string"}, "includeSubtasks": {"type": "boolean"}}, "required": []}),
            tool("task_get", "Get task by ID", {"type": "object", "properties": {"taskId": {"type": "string"}}, "required": ["taskId"]}),
            tool("task_next", "Next recommended task"),
        ]

        # Task modifications
        tools += [
            tool("task_add", "Create task", {"type": "object", "properties": {"title": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "string"}}, "required": ["title", "description"]}),
            tool("task_update", "Update task", {"type": "object", "properties": {"taskId": {"type": "string"}, "updates": {"type": "object"}}, "required": ["taskId", "updates"]}),
            tool("task_status", "Change task status", {"type": "object", "properties": {"taskId": {"type": "string"}, "status": {"type": "string"}}, "required": ["taskId", "status"]}),
            tool("task_sub_add", "Add subtask", {"type": "object", "properties": {"parentId": {"type": "string"}, "title": {"type": "string"}, "description": {"type": "string"}}, "required": ["parentId", "title", "description"]}),
            tool("task_sub_upd", "Append subtask notes", {"type": "object", "properties": {"taskId": {"type": "string"}, "notes": {"type": "string"}}, "required": ["taskId", "notes"]}),
            tool("task_multi", "Batch update starting from ID", {"type": "object", "properties": {"fromId": {"type": "string"}, "updates": {"type": "object"}}, "required": ["fromId", "updates"]}),
            tool("task_remove", "Delete task", {"type": "object", "properties": {"taskId": {"type": "string"}}, "required": ["taskId"]}),
        ]

        # Docs
        tools += [
            tool("doc_generate", "Generate task documentation", {"type": "object", "properties": {"taskId": {"type": "string"}, "content": {"type": "string"}}, "required": ["taskId"]}),
            tool("doc_quality", "Score doc quality", {"type": "object", "properties": {"taskId": {"type": "string"}}, "required": ["taskId"]}),
            tool("doc_refs", "List doc references", {"type": "object", "properties": {"taskId": {"type": "string"}}, "required": ["taskId"]}),
            tool("doc_research", "Doc research (basic)", {"type": "object", "properties": {"taskId": {"type": "string"}, "query": {"type": "string"}}, "required": ["taskId"]}),
            tool("doc_comply", "Doc compliance check", {"type": "object", "properties": {"taskId": {"type": "string"}, "framework": {"type": "string"}}, "required": ["taskId"]}),
        ]

        # Enhanced Research
        tools += [
            tool("research", "Enhanced research (package)", {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}),
        ]

        # Plan parser
        tools += [
            tool("plan_parse", "Parse atomic plan", {"type": "object", "properties": {"plan_file": {"type": "string"}, "dry_run": {"type": "boolean"}}, "required": ["plan_file"]}),
            tool("plan_list", "List plans", {"type": "object", "properties": {"search_path": {"type": "string"}}, "required": []}),
            tool("plan_validate", "Validate plan format", {"type": "object", "properties": {"plan_file": {"type": "string"}}, "required": ["plan_file"]}),
        ]

        # Linting (basic + enhanced)
        tools += [
            tool("lint_full", "Run full lint"),
            tool("lint_bg", "Run lint in background"),
            tool("lint_supa", "Run Supabase-specific lint"),
            tool("lint_status", "Lint status"),
            tool("lint_trigger", "Trigger lint", {"type": "object", "properties": {"reason": {"type": "string"}}, "required": []}),
            tool("watch_start", "Start rules watcher"),
            tool("watch_status", "Rules watcher status"),
            tool("enh_full_lint", "Run enhanced lint"),
            tool("enh_pattern", "Enhanced pattern learning"),
            tool("enh_autofix", "Enhanced autofix", {"type": "object", "properties": {"target_files": {"type": "array", "items": {"type": "string"}}}, "required": []}),
            tool("enh_perf", "Enhanced performance protection"),
            tool("enh_rag", "Enhanced RAG compliance"),
            tool("enh_mon_start", "Start enhanced monitoring"),
            tool("enh_mon_stop", "Stop enhanced monitoring"),
            tool("enh_status", "Enhanced status"),
        ]

        # Testing
        tools += [
            tool("test_analyze", "Analyze test suite"),
            tool("test_delete_flaky", "Delete flaky tests", {"type": "object", "properties": {"confirmation": {"type": "boolean"}}, "required": []}),
            tool("test_confidence", "Test confidence report"),
        ]

        return tools

    @staticmethod
    def get_version_info() -> Dict[str, Any]:
        total = len(ToolRegistry.get_tools_for_mcp())
        return {
            "mcp_server_version": "1.0.0",
            "api_version": "1.0.0",
            "supported_versions": ["1.0.0"],
            "next_version": "2.0.0",
            "deprecation_date": "2025-12-31T23:59:59Z",
            "versioning_standard": "CEREBRAL_191_INTEGRATION_API_VERSIONING_STANDARDS.md",
            "total_tools": total,
            "version_metadata": {
                "semantic_versioning": True,
                "backward_compatibility": True,
                "migration_support": True,
                "enterprise_grade": True,
            },
        }


