"""GDSFactory+ Logger."""

from __future__ import annotations

import sys
from functools import cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias

if TYPE_CHECKING:
    import loguru

    import gdsfactoryplus.project as gfp_project
    import gdsfactoryplus.settings as gfp_settings
else:
    from gdsfactoryplus.lazy import lazy_import

    loguru = lazy_import("loguru")
    gfp_project = lazy_import("gdsfactoryplus.project")
    gfp_settings = lazy_import("gdsfactoryplus.settings")

__all__ = ["Logger", "fix_log_line_numbers", "get_logger"]

Logger: TypeAlias = Any  # TODO: create proper type for Logger


@cache
def get_logger() -> Logger:
    """Get the GDSFactory+ logger."""
    return _setup_logger()


def fix_log_line_numbers(content: str) -> str:
    """Patches a different format for file + line nr combination into logs."""
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if '", line ' in line:
            first, rest = line.split('", line ')
            nbr, rest = rest.split(",")
            lines[i] = f'{first}:{nbr}",{rest}'
    return "\n".join(lines)


def _setup_logger() -> Logger:
    """Logger setup."""
    settings = gfp_settings.get_settings()

    project_dir = Path(
        gfp_project.maybe_find_docode_project_dir() or Path.cwd()
    ).resolve()
    ws_port_path = Path(project_dir) / "build" / "log" / "_server.log"
    ws_port_path.parent.mkdir(parents=True, exist_ok=True)
    ws_port_path.touch(exist_ok=True)
    loguru.logger.remove()
    _format = "{time:HH:mm:ss} | {level: <8} | {message}"
    ws_port_path.parent.mkdir(parents=True, exist_ok=True)
    loguru.logger.add(
        sys.stdout, level=settings.log.level, colorize=True, format=_format
    )
    loguru.logger.add(
        RotatingFileHandler(ws_port_path, maxBytes=20 * 1024 * 1024, backupCount=14),
        level=settings.log.debug_level,
        format=_format,
    )
    return loguru.logger
