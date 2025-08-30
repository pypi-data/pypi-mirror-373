"""Find the GDSFactory+ project folder."""

from __future__ import annotations

from pathlib import Path

__all__ = ["find_docode_project_dir", "maybe_find_docode_project_dir"]


def find_docode_project_dir() -> Path:
    """Find the GDSFactory+ project folder, return None if not found."""
    path = maybe_find_docode_project_dir()
    if path is None:
        msg = "No project dir found."
        raise FileNotFoundError(msg)
    return path


def maybe_find_docode_project_dir() -> Path | None:
    """Find the GDSFactory+ project folder, raise FileNotFoundErorr if not found."""
    maybe_pyproject = Path.cwd().resolve() / "pyproject.toml"
    while not maybe_pyproject.is_file():
        prev_pyproject = maybe_pyproject
        maybe_pyproject = maybe_pyproject.parent.parent / "pyproject.toml"
        if prev_pyproject == maybe_pyproject:
            break
    if maybe_pyproject.is_file():
        return maybe_pyproject.parent
    return None
