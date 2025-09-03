"""GDSFactory+ Logger."""

from __future__ import annotations

import logging
import sys
from functools import cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias, cast

if TYPE_CHECKING:
    import loguru
    import uvicorn
    from loguru._logger import Logger

    import gdsfactoryplus.models as m
    import gdsfactoryplus.project as gfp_project
    import gdsfactoryplus.settings as gfp_settings
    from gdsfactoryplus.core.communication import send_message
else:
    from gdsfactoryplus.core.lazy import lazy_import

    uvicorn = lazy_import("uvicorn")
    Logger: TypeAlias = Any
    loguru = lazy_import("loguru")
    gfp_project = lazy_import("gdsfactoryplus.project")
    gfp_settings = lazy_import("gdsfactoryplus.settings")
    m = lazy_import("gdsfactoryplus.models")
    send_message = lazy_import("gdsfactoryplus.core.communication", "send_message")

__all__ = ["Logger", "get_logger"]


@cache
def get_logger(source: str = "server") -> Logger:
    """Get the GDSFactory+ logger."""
    logger = _setup_logger(source=source)
    logger.debug("GDSFactory+ logger initialized.")
    return logger


def _setup_logger(source: str = "server") -> Logger:
    """Logger setup."""
    settings = gfp_settings.get_settings()

    project_dir = Path(gfp_project.maybe_find_project_dir() or Path.cwd()).resolve()
    serve_log_path = Path(project_dir) / "build" / "log" / "_server.log"
    serve_log_path.parent.mkdir(parents=True, exist_ok=True)
    serve_log_path.touch(exist_ok=True)
    loguru.logger.remove()
    _format = "{time:HH:mm:ss} | {level: <8} | {message}"
    _console_format = (
        "<blue>{time:HH:mm:ss}</blue> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    _file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS}"
        " | {level: <8}"
        " | {name}:{function}:{line}"
        " | {message}"
    )
    serve_log_path.parent.mkdir(parents=True, exist_ok=True)
    loguru.logger.add(
        sys.stdout,
        level=settings.log.level,
        colorize=True,
        format=_console_format,
    )
    loguru.logger.add(
        RotatingFileHandler(serve_log_path, maxBytes=20 * 1024 * 1024, backupCount=14),
        level=settings.log.debug_level,
        format=_file_format,
        colorize=False,
    )
    # Add VS Code log handler
    vscode_handler = VSCodeLogHandler(source=source)
    loguru.logger.add(
        vscode_handler.write,
        level=settings.log.level,
        format=_format,
        colorize=False,
    )
    loguru.logger.level("DEBUG", color="<italic><cyan><normal>")
    loguru.logger.level("INFO", color="<normal>")
    loguru.logger.level("SUCCESS", color="<green><bold>")
    loguru.logger.level("WARNING", color="<yellow><normal>")
    loguru.logger.level("ERROR", color="<red><normal>")
    loguru.logger.level("CRITICAL", color="<RED><bold>")
    logging.getLogger().handlers = [UvicornInterceptHandler()]
    logging.getLogger("uvicorn").handlers = [UvicornInterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [UvicornInterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [UvicornInterceptHandler()]
    return cast(Logger, loguru.logger)


class VSCodeLogHandler:
    """Custom handler to send log messages to VS Code."""

    def __init__(self, source: str = "server") -> None:
        """Initialize the VSCode log handler."""
        self.source = source

    def write(self, message: str) -> None:
        """Handle log messages from loguru."""
        parts = message.strip().split(" | ", 2)
        if len(parts) >= 3:
            level_str = parts[1].strip().lower()
            log_message = parts[2]

            # Map loguru levels to our LogMessage levels
            level_mapping = {
                "debug": "debug",
                "info": "info",
                "success": "info",  # Map success to info
                "warning": "warning",
                "error": "error",
                "critical": "error",  # Map critical to error
            }

            mapped_level = level_mapping.get(level_str, "info")

            # Create and send the LogMessage
            log_msg = m.LogMessage(
                level=cast(m.LogLevel, mapped_level),
                message=log_message,
                source=self.source,
            )
            send_message(log_msg)


class UvicornInterceptHandler(logging.Handler):
    def emit(self, record: Any) -> None:
        try:
            level = get_logger().level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger_opt = get_logger().opt(depth=6, exception=record.exc_info)
        logger_opt.log(level, record.getMessage())
