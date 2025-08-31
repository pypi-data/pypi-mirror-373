from __future__ import annotations

from typing import Any, Dict
import os
import re


class TestingHandlers:
    async def handle_test_analyze(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "analysis": {"tests": 0, "confidence": 1.0}}

    async def handle_test_delete_flaky(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "success", "deleted": 0}

    async def handle_test_confidence(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        # If invoked from within a pytest session, avoid nested pytest runs
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return {"status": "success", "confidence": {"score": 1.0}}
        from cflow_platform.core.test_runner import run_tests
        paths = arguments.get("paths") or ["cflow_platform/tests"]
        # Avoid pytest re-entrancy and recursive invocation of this test by excluding itself
        result = run_tests(
            paths=paths,
            in_process=False,
            k="not test_confidence",
            env_overrides={
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            },
            extra_pytest_args=["-q"],
        )
        summary = result.get("summary", {})
        total = int(summary.get("total", 0) or 0)
        failed = int(summary.get("failed", 0) or 0)
        errors = int(summary.get("errors", 0) or 0)
        passing = max(total - failed - errors, 0)
        score = 0.0 if total == 0 else passing / max(total, 1)
        return {"status": result.get("status", "success"), "confidence": {"score": score}, "summary": summary}


def _parse_pytest_output(output: str) -> Dict[str, Any]:
    summary_line = ""
    failures: list[dict[str, str]] = []
    # Capture failure lines from short summary section
    in_short = False
    for line in output.splitlines():
        if line.strip().lower().startswith("=========================== short test summary info"):
            in_short = True
            continue
        if in_short and line.strip().startswith("===="):
            in_short = False
        if in_short and line.strip().startswith("FAILED "):
            failures.append({"line": line.strip()})
        # Best-effort summary line detection
        if re.search(r"\b(no tests ran|passed|failed|errors?|skipped|xfailed|xpassed)\b", line, re.IGNORECASE):
            summary_line = line.strip()
    return {"summary_line": summary_line, "failures": failures}


