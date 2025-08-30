"""Find the GDSFactory+ project folder."""

from __future__ import annotations

from pathlib import Path

__all__ = ["find_project_dir", "maybe_find_project_dir"]


def find_project_dir() -> Path:
    """Find the GDSFactory+ project folder.

    Returns:
        The path to the GDSFactory+ project folder.

    Raises:
        FileNotFoundError: if no project dir is found.
    """
    path = maybe_find_project_dir()
    if path is None:
        msg = "No project dir found."
        raise FileNotFoundError(msg)
    return path


def maybe_find_project_dir() -> Path | None:
    """Maybe find the GDSFactory+ project folder.

    Returns:
        The path to the GDSFactory+ project folder or None if not found.
    """
    maybe_pyproject = Path.cwd().resolve() / "pyproject.toml"
    while not maybe_pyproject.is_file():
        prev_pyproject = maybe_pyproject
        maybe_pyproject = maybe_pyproject.parent.parent / "pyproject.toml"
        if prev_pyproject == maybe_pyproject:
            break
    if maybe_pyproject.is_file():
        return maybe_pyproject.parent
    return None
