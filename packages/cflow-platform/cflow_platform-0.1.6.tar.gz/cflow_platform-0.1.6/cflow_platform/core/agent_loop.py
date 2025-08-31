from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json
import os
import sys
import time
from pathlib import Path

from .public_api import get_direct_client_executor
from .test_runner import run_tests


@dataclass
class InstructionProfile:
    name: str
    description: str
    goals: List[str]
    test_paths: List[str]
    verify_mode: str = "tests"


DEFAULT_PROFILES: Dict[str, InstructionProfile] = {
    "quick": InstructionProfile(
        name="quick",
        description="Fast feedback profile running unit tests",
        goals=["plan", "apply", "verify"],
        test_paths=["cflow_platform/tests"],
        verify_mode="tests",
    ),
}


def plan(profile: InstructionProfile) -> Dict[str, Any]:
    return {
        "status": "success",
        "plan": [
            {"step": 1, "action": "run-tests", "paths": profile.test_paths},
        ],
    }


def verify(profile: InstructionProfile) -> Dict[str, Any]:
    if profile.verify_mode == "tests":
        result = run_tests(paths=profile.test_paths, use_uv=False, in_process=True)
        return {
            "status": result.get("status"),
            "verification": result,
        }
    return {"status": "error", "message": f"Unknown verify mode {profile.verify_mode}"}


def loop(profile_name: str, max_iterations: int = 1) -> Dict[str, Any]:
    profile = DEFAULT_PROFILES.get(profile_name)
    if not profile:
        return {"status": "error", "message": f"Unknown profile {profile_name}"}
    executor = get_direct_client_executor()
    history: List[Dict[str, Any]] = []
    for i in range(max_iterations):
        p = plan(profile)
        history.append({"iteration": i + 1, "planning": p})
        v = verify(profile)
        history[-1]["verify"] = v
        if v.get("status") == "success":
            break
    return {"status": history[-1]["verify"].get("status", "error"), "iterations": len(history), "history": history}


def cli() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Unified CLI agent loop for cflow-platform")
    parser.add_argument("--profile", default="quick", help="Instruction profile name")
    parser.add_argument("--max-iter", type=int, default=1, help="Maximum loop iterations")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON result")
    args = parser.parse_args()
    result = loop(args.profile, max_iterations=args.max_iter)
    if args.json:
        print(json.dumps(result))
    else:
        status = result.get("status")
        print(f"Agent loop finished with status={status} after {result.get('iterations')} iteration(s)")
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(cli())


