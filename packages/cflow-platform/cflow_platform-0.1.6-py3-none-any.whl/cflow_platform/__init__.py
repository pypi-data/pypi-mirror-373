"""CFlow Platform package (Phase 1 wrapper for extraction)."""

__version__ = "0.1.5"

__all__ = [
    "public_api",
    "core_public_api",
]

# Expose Phase 2 core namespace for convenience
from .core import public_api as core_public_api  # type: ignore


