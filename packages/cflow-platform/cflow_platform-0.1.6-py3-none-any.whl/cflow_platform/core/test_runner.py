from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import os
import re
import shutil
import subprocess
import sys
import time


def _build_pytest_args(paths: Optional[List[str]], k: Optional[str], m: Optional[str], maxfail: int, verbose: bool, extra: Optional[List[str]] | None) -> List[str]:
    args: List[str] = []
    if verbose:
        args.append("-vv")
    else:
        args.append("-q")
    if maxfail and maxfail > 0:
        args.append(f"--maxfail={maxfail}")
    args.append("-rA")
    if k:
        args.extend(["-k", k])
    if m:
        args.extend(["-m", m])
    if extra:
        args.extend(extra)
    if paths and len(paths) > 0:
        args.extend(paths)
    return args


def _parse_summary_from_text(output: str) -> Dict[str, int]:
    summary: Dict[str, int] = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "xpassed": 0,
    }
    pattern = re.compile(r"(?:(\d+)\s+passed)?(?:,\s*)?(?:(\d+)\s+failed)?(?:,\s*)?(?:(\d+)\s+errors?)?(?:,\s*)?(?:(\d+)\s+skipped)?(?:,\s*)?(?:(\d+)\s+xfailed)?(?:,\s*)?(?:(\d+)\s+xpassed)?", re.IGNORECASE)
    for line in output.splitlines():
        m = pattern.search(line)
        if m:
            groups = m.groups(default="0")
            summary["passed"] = max(summary["passed"], int(groups[0] or 0))
            summary["failed"] = max(summary["failed"], int(groups[1] or 0))
            summary["errors"] = max(summary["errors"], int(groups[2] or 0))
            summary["skipped"] = max(summary["skipped"], int(groups[3] or 0))
            summary["xfailed"] = max(summary["xfailed"], int(groups[4] or 0))
            summary["xpassed"] = max(summary["xpassed"], int(groups[5 or 0]))
    return summary


def run_tests(
    paths: Optional[List[str]] = None,
    k: Optional[str] = None,
    m: Optional[str] = None,
    maxfail: int = 0,
    cwd: Optional[str] = None,
    use_uv: bool = False,
    in_process: bool = True,
    timeout_sec: Optional[int] = None,
    verbose: bool = False,
    extra_pytest_args: Optional[List[str]] = None,
    env_overrides: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    start = time.perf_counter()
    if in_process:
        try:
            import pytest  # type: ignore
        except Exception as e:
            in_process = False
    if in_process:
        test_results: List[Dict[str, Any]] = []
        summary: Dict[str, int] = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0,
        }

        class Collector:
            def __init__(self) -> None:
                self.results: List[Dict[str, Any]] = []

            def pytest_runtest_logreport(self, report):  # type: ignore[no-redef]
                if report.when != "call" and report.outcome == "failed":
                    outcome_key = "errors"
                    summary[outcome_key] += 1
                if report.when != "call":
                    return
                item: Dict[str, Any] = {
                    "nodeid": getattr(report, "nodeid", None),
                    "outcome": report.outcome,
                    "duration_sec": getattr(report, "duration", None),
                }
                if hasattr(report, "longreprtext") and report.outcome != "passed":
                    item["longrepr"] = report.longreprtext  # type: ignore[attr-defined]
                self.results.append(item)
                if report.outcome in summary:
                    summary[report.outcome] += 1
                elif report.outcome == "xfailed":
                    summary["xfailed"] += 1
                elif report.outcome == "xpassed":
                    summary["xpassed"] += 1

        plugin = Collector()
        args = _build_pytest_args(paths, k, m, maxfail, verbose, extra_pytest_args)
        try:
            code = pytest.main(args, plugins=[plugin])  # type: ignore[name-defined]
        except SystemExit as se:
            code = int(getattr(se, "code", 2))
        duration = time.perf_counter() - start
        test_results = plugin.results
        status = "success" if code == 0 else "failure"
        return {
            "status": status,
            "summary": {
                **summary,
                "total": sum(summary.values()),
                "exit_code": code,
            },
            "duration_sec": duration,
            "tests": test_results,
        }

    cmd: List[str] = []
    if use_uv and shutil.which("uv"):
        cmd.extend(["uv", "run"]) 
        cmd.append("pytest")
    else:
        cmd.extend([sys.executable, "-m", "pytest"]) 
    cmd.extend(_build_pytest_args(paths, k, m, maxfail, verbose, extra_pytest_args))
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec,
            check=False,
            env={**os.environ, **(env_overrides or {})},
        )
    except subprocess.TimeoutExpired as te:
        duration = time.perf_counter() - start
        return {
            "status": "failure",
            "error": "timeout",
            "duration_sec": duration,
            "stdout": te.stdout,
            "stderr": te.stderr,
        }
    duration = time.perf_counter() - start
    output = proc.stdout + "\n" + proc.stderr
    summary = _parse_summary_from_text(output)
    status = "success" if proc.returncode == 0 else "failure"
    return {
        "status": status,
        "summary": {
            **summary,
            "total": sum(summary.values()),
            "exit_code": proc.returncode,
        },
        "duration_sec": duration,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def cli() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Run pytest and emit structured JSON results")
    parser.add_argument("paths", nargs="*", help="Test paths to run")
    parser.add_argument("--k", dest="k", help="Pytest -k expression", default=None)
    parser.add_argument("--m", dest="m", help="Pytest -m marker expression", default=None)
    parser.add_argument("--maxfail", type=int, default=0)
    parser.add_argument("--use-uv", action="store_true")
    parser.add_argument("--timeout", type=int, default=None)
    parser.add_argument("--no-in-process", dest="in_process", action="store_false")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--extra", nargs=argparse.REMAINDER, help="Extra args after --", default=None)
    args = parser.parse_args()
    extra = None
    if args.extra:
        extra = [a for a in args.extra if a != "--"]
    result = run_tests(
        paths=args.paths or None,
        k=args.k,
        m=args.m,
        maxfail=args.maxfail,
        use_uv=args.use_uv,
        in_process=args.in_process,
        timeout_sec=args.timeout,
        verbose=args.verbose,
        extra_pytest_args=extra,
    )
    print(json.dumps(result))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(cli())


