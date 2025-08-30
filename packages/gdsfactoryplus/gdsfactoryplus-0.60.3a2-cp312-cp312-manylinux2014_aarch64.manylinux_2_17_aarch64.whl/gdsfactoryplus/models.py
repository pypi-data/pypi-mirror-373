"""GDSFactory+ Pydantic models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self, TypeAlias

import pydantic as pyd

if TYPE_CHECKING:
    import kfactory as kf
else:
    from gdsfactoryplus.core.lazy import lazy_import

    kf = lazy_import("kfactory")


LogLevel: TypeAlias = Literal["debug", "info", "warning", "error"]

PdkType: TypeAlias = Literal["pdk", "base_pdk"]


class User(pyd.BaseModel):
    """User class containing user information from GDSFactory+."""

    user_name: str
    email: str
    organization_name: str | None
    organization_id: str | None
    pdks: list[str] | None
    is_superuser: bool


class FactoryRecord(pyd.BaseModel):
    """Represents a factory record for the database."""

    name: str
    source: str | None
    status: str
    message: str
    default_settings: str = "{}"
    pdk_type: PdkType = "pdk"
    parents: str = "[]"
    children: str = "[]"
    is_partial: bool = False
    last_updated: str = ""  # Will be set automatically by database

    def absolute_source(self) -> Path | None:
        """Return the absolute path to the source file."""
        if self.source is None:
            return None
        if Path(self.source).is_absolute():
            return Path(self.source).resolve()
        from .settings import get_project_dir

        return get_project_dir() / self.source

    def default_settings_dict(self) -> dict[str, Any]:
        """Return the default settings as a dictionary."""
        return json.loads(self.default_settings)

    def parents_list(self) -> list[str]:
        """Return the parents as a list."""
        return json.loads(self.parents)

    def children_list(self) -> list[str]:
        """Return the children as a list."""
        return json.loads(self.children)

    def to_db_tuple(self) -> tuple:
        """Convert to tuple for database insertion, excluding last_updated."""
        return (
            self.name,
            self.source,
            self.status,
            self.message,
            self.default_settings,
            self.pdk_type,
            self.parents,
            self.children,
            self.is_partial,
        )


class ComponentRecord(pyd.BaseModel):
    """Represents a component record for the database."""

    name: str
    factory_name: str  # foreign key
    ports: str
    settings: str
    info: str

    def ports_list(self) -> list[str]:
        """Return the ports as a list."""
        return json.loads(self.ports)

    def settings_dict(self) -> dict[str, Any]:
        """Return the settings as a dictionary."""
        return json.loads(self.settings)

    def info_dict(self) -> dict[str, Any]:
        """Return the info as a dictionary."""
        return json.loads(self.info)

    def to_db_tuple(self) -> tuple:
        """Convert to tuple for database insertion."""
        return (
            self.name,
            self.factory_name,
            self.ports,
            self.settings,
            self.info,
        )

    @classmethod
    def from_tkcell(cls, tkcell: Any) -> Self:
        """Create a ComponentRecord from a TKCell object."""
        ports = object.__getattribute__(tkcell, "ports")
        port_names = json.dumps([str(p.name) for p in ports])
        factory_name = (
            getattr(tkcell, "basename", "")
            or getattr(tkcell, "function_name", "")
            or ""
        )
        default_settings = kf.KCellSettings()
        settings = getattr(tkcell, "settings", default_settings).model_dump_json()
        info = getattr(tkcell, "info", default_settings).model_dump_json()
        return cls(
            name=tkcell.name,
            factory_name=factory_name,
            ports=port_names,
            settings=settings,
            info=info,
        )


class ReloadSchematicMessage(pyd.BaseModel):
    """A message to vscode to trigger a schematic reload."""

    what: Literal["reloadSchematic"] = "reloadSchematic"
    path: str

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.path))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ReloadSchematicMessage):
            return False
        return self.what == other.what and self.path == other.path


class ReloadFactoriesMessage(pyd.BaseModel):
    """A message to vscode to trigger a pics tree reload."""

    what: Literal["reloadFactories"] = "reloadFactories"

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash(self.what)

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ReloadFactoriesMessage):
            return False
        return self.what == other.what


class RestartServerMessage(pyd.BaseModel):
    """A message to vscode to trigger a server restart."""

    what: Literal["restartServer"] = "restartServer"

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash(self.what)

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, RestartServerMessage):
            return False
        return self.what == other.what


class ReloadLayoutMessage(pyd.BaseModel):
    """A message to vscode to trigger a gds viewer reload."""

    what: Literal["reloadLayout"] = "reloadLayout"
    cell: str

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.cell))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, ReloadLayoutMessage):
            return False
        return self.what == other.what and self.cell == other.cell


class LogMessage(pyd.BaseModel):
    """A message to vscode to log a message."""

    what: Literal["log"] = "log"
    level: LogLevel
    message: str

    def __hash__(self) -> int:
        """Return hash of the message for deduplication."""
        return hash((self.what, self.level, self.message))

    def __eq__(self, other: object) -> bool:
        """Check equality for deduplication."""
        if not isinstance(other, LogMessage):
            return False
        return (
            self.what == other.what
            and self.level == other.level
            and self.message == other.message
        )


Message: TypeAlias = (
    ReloadFactoriesMessage
    | ReloadLayoutMessage
    | RestartServerMessage
    | ReloadSchematicMessage
    | LogMessage
)
