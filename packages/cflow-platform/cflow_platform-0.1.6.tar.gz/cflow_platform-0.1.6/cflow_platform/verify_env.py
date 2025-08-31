"""Wrapper for scripts/verify_env.py to stabilize import/CLI usage."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _load_monorepo_verifier():
    """Try to load the monorepo verifier when running inside the repo."""
    base = Path.cwd()
    ve = base / "scripts" / "verify_env.py"
    if ve.exists():
        spec = importlib.util.spec_from_file_location("verify_env", str(ve))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[attr-defined]
            return module
    return None


# Fallback portable implementation (mirrors monorepo script)
def load_dotenv_files(paths: List[str]) -> Dict[str, str]:
    env: Dict[str, str] = {}
    for p in paths:
        try:
            fp = Path(p)
            if not fp.is_file():
                continue
            for line in fp.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip().strip('"').strip("'")
        except Exception:
            continue
    return env


def merge_env(file_env: Dict[str, str]) -> Dict[str, str]:
    merged = dict(file_env)
    merged.update(os.environ)
    return merged


LLM_KEYS = [
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "PERPLEXITY_API_KEY",
    "GOOGLE_API_KEY",
    "XAI_API_KEY",
    "MISTRAL_API_KEY",
    "OPENROUTER_API_KEY",
]


def required_keys_for_mode(mode: str) -> Tuple[List[str], List[List[str]]]:
    mode = mode.lower()
    if mode == "runtime":
        return (["SUPABASE_URL", "SUPABASE_ANON_KEY", "CEREBRAL_TENANT_ID"], [])
    if mode == "migrations":
        return (["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"], [])
    if mode in ("ragkg", "rag", "kg"):
        return (["SUPABASE_URL", "CEREBRAL_TENANT_ID"], [["SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY"]])
    if mode == "llm":
        return ([], [LLM_KEYS])
    if mode in ("mcp", "installer"):
        return (["CEREBRAL_TENANT_ID", "CEREBRAL_USER_ID"], [])
    return ([], [])


def check_modes(env: Dict[str, str], modes: List[str]) -> Dict[str, Dict[str, List[str]]]:
    report: Dict[str, Dict[str, List[str]]] = {}
    for mode in modes:
        req_all, req_any_groups = required_keys_for_mode(mode)
        missing_all = [k for k in req_all if not env.get(k)]
        missing_any_groups: List[str] = []
        for group in req_any_groups:
            if not any(env.get(k) for k in group):
                missing_any_groups.append("one_of(" + ",".join(group) + ")")
        report[mode] = {"missing_all": missing_all, "missing_one_of": missing_any_groups}
    return report


def _common_main(args: argparse.Namespace) -> int:
    paths: List[str] = []
    if args.scope in ("root", "both"):
        paths.append(".env")
    if args.scope in ("cflow", "both"):
        paths.append(".cerebraflow/.env")
    file_env = load_dotenv_files(paths)
    env = merge_env(file_env)
    report = check_modes(env, args.mode)
    ok = all(not r["missing_all"] and not r["missing_one_of"] for r in report.values())
    output = {
        "ok": ok,
        "modes": args.mode,
        "scope": args.scope,
        "loaded_paths": [p for p in paths if Path(p).is_file()],
        "report": report,
    }
    print(json.dumps(output))
    return 0 if ok else 1


def cli() -> int:
    """Console script entrypoint compatible with pyproject scripts."""
    ve = _load_monorepo_verifier()
    if ve is not None:
        return ve.main()
    parser = argparse.ArgumentParser(description="Verify required environment keys for operations")
    parser.add_argument("--mode", action="append", required=True,
                        help="Operation mode: runtime, migrations, ragkg, llm, mcp, installer (repeatable)")
    parser.add_argument("--scope", choices=["root", "cflow", "both"], default="both",
                        help="Which .env files to load in addition to OS env")
    return _common_main(parser.parse_args())


if __name__ == "__main__":
    sys.exit(cli())


