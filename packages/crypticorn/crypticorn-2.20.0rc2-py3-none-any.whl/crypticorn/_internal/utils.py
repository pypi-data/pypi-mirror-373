"""General utility functions and client helper methods used across the codebase."""

from typing import Any


def optional_import(module_name: str, extra_name: str) -> Any:
    """
    Tries to import a module. Raises `ImportError` if not found with a message to install the extra dependency.
    """
    try:
        return __import__(module_name)
    except ImportError as e:
        raise ImportError(
            f"Optional dependency '{module_name}' is required for this feature. "
            f"Install it with: pip install crypticorn[{extra_name}]"
        ) from e
