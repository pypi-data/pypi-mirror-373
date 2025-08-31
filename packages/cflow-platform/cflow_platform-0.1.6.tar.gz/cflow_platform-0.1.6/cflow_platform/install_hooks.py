"""Wrapper to install enhanced git hooks via the monorepo script."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def install() -> int:
    root = Path(__file__).resolve().parents[2]
    hooks_dir = root / "git-hooks"
    script = root / "scripts" / "install-enhanced-git-hooks.sh"

    if script.exists():
        proc = subprocess.run(["bash", str(script)], cwd=root)
        return proc.returncode

    # Seed hooks from assets when repo script not found (fresh environments)
    assets = Path(__file__).resolve().parent / "assets" / "git-hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    for name in ("enhanced-pre-commit", "enhanced-post-commit"):
        src = assets / name
        dst = hooks_dir / name
        if not dst.exists():
            shutil.copyfile(src, dst)
            os.chmod(dst, 0o755)
    print("[cflow-platform] Seeded git-hooks assets. Please rerun once repo script is available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(install())


