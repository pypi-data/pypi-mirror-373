from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import difflib
import json
import os
import shutil
from pathlib import Path


@dataclass
class EditPlan:
    file: str
    original_snippet: str
    replacement_snippet: str


@dataclass
class ApplyOptions:
    dry_run: bool = True
    allowlist: Optional[List[str]] = None  # directories or file globs
    backup_dir: Optional[str] = None


def _is_allowed(path: Path, allowlist: Optional[List[str]]) -> bool:
    if not allowlist:
        return True
    p = str(path)
    for rule in allowlist:
        if rule in p:
            return True
    return False


def _apply_single_edit(content: str, original: str, replacement: str) -> Tuple[str, bool]:
    if original not in content:
        return content, False
    return content.replace(original, replacement, 1), True


def _diff_text(before: str, after: str, file: str) -> str:
    return "\n".join(
        difflib.unified_diff(before.splitlines(), after.splitlines(), fromfile=f"a/{file}", tofile=f"b/{file}", lineterm="")
    )


def apply_minimal_edits(edits: List[EditPlan], options: Optional[ApplyOptions] = None) -> Dict[str, Any]:
    options = options or ApplyOptions()
    results: List[Dict[str, Any]] = []
    backups: List[str] = []
    for ep in edits:
        path = Path(ep.file)
        if not _is_allowed(path, options.allowlist):
            results.append({"file": ep.file, "status": "skipped", "reason": "not allowed"})
            continue
        if not path.exists():
            results.append({"file": ep.file, "status": "error", "reason": "missing file"})
            continue
        before = path.read_text()
        after, changed = _apply_single_edit(before, ep.original_snippet, ep.replacement_snippet)
        diff = _diff_text(before, after, ep.file)
        if not changed:
            results.append({"file": ep.file, "status": "noop", "diff": diff})
            continue
        if options.dry_run:
            results.append({"file": ep.file, "status": "dry-run", "diff": diff})
            continue
        if options.backup_dir:
            backup_dir = Path(options.backup_dir)
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / (path.name + ".bak")
            backup_path.write_text(before)
            backups.append(str(backup_path))
        path.write_text(after)
        results.append({"file": ep.file, "status": "applied", "diff": diff})
    return {"status": "success", "results": results, "backups": backups}


def rollback(backups: List[str]) -> Dict[str, Any]:
    restored: List[str] = []
    for b in backups:
        bp = Path(b)
        if not bp.exists():
            continue
        target = bp.with_suffix("")
        if target.exists():
            target.write_text(bp.read_text())
            restored.append(str(target))
    return {"status": "success", "restored": restored}


