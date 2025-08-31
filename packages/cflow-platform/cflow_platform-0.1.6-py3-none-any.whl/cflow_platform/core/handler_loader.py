from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from types import ModuleType


def load_handler_module(module_name: str) -> ModuleType:
    """Load a handler module by name with package-first, monorepo-fallback resolution."""
    # Try local package handlers first
    try:
        return import_module(f"cflow_platform.handlers.{module_name}")  # type: ignore
    except Exception:
        pass

    # Fallback to monorepo handlers path
    base = Path(__file__).resolve().parents[3]  # .../cflow-platform/
    mono_path = base.parent / ".cerebraflow" / "core" / "mcp" / "handlers" / f"{module_name}.py"
    spec = spec_from_file_location(f"cflow_handlers_{module_name}", str(mono_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot locate handler module: {module_name}")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


