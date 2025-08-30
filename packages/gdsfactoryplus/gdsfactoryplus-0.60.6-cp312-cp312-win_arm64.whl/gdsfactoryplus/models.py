"""GDSFactory+ Pydantic models."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypeAlias, cast

from gdsfactoryplus.lazy import lazy_import

if TYPE_CHECKING:
    import pydantic as pyd
    import sax
    import yaml
    from gdsfactory.read.from_yaml import from_yaml

    import gdsfactoryplus.core.shared as gfp_shared
    import gdsfactoryplus.project as gfp_project
    import gdsfactoryplus.settings as gfp_settings
else:
    yaml = lazy_import("yaml")
    sax = lazy_import("sax")
    pyd = lazy_import("pydantic")
    from_yaml = lazy_import("gdsfactory.read.from_yaml", "from_yaml")
    gfp_shared = lazy_import("gdsfactoryplus.core.shared")
    gfp_settings = lazy_import("gdsfactoryplus.settings")
    gfp_project = lazy_import("gdsfactoryplus.project")

__all__ = [
    "DoItForMe",
    "ErrorMessage",
    "Message",
    "MimeType",
    "RefreshTreesMessage",
    "ReloadLayoutMessage",
    "ReloadSchematicMessage",
    "RestartServerMessage",
    "Result",
    "ShowGdsMessage",
    "ShowMessage",
    "SimulationConfig",
    "SimulationData",
    "UpdateProgressMessage",
    "User",
    "ensure_recursive_netlist",
]

MimeType = Literal[
    "html", "json", "yaml", "plain", "base64", "png", "gds", "netlist", "dict", "error"
]


class ShowMessage(pyd.BaseModel):
    """A message to vscode to show an object."""

    what: Literal["show"] = "show"  # do not override
    mime: MimeType
    content: str


class ShowGdsMessage(pyd.BaseModel):
    """A message to vscode to show a GDS."""

    what: Literal["showGds"] = "showGds"  # do not override
    gds: str
    lyrdb: str


class ReloadSchematicMessage(pyd.BaseModel):
    """A message to vscode to trigger a schematic reload."""

    what: Literal["reloadSchematic"] = "reloadSchematic"
    path: str


class ErrorMessage(pyd.BaseModel):
    """A message to vscode to trigger an error popup."""

    what: Literal["error"] = "error"  # do not override
    category: str
    message: str
    path: str


class RefreshTreesMessage(pyd.BaseModel):
    """A message to vscode to trigger a pics tree reload."""

    what: Literal["refreshPicsTree"] = "refreshPicsTree"


class RestartServerMessage(pyd.BaseModel):
    """A message to vscode to trigger a server restart."""

    what: Literal["restartServer"] = "restartServer"


class ReloadLayoutMessage(pyd.BaseModel):
    """A message to vscode to trigger a gds viewer reload."""

    what: Literal["reloadLayout"] = "reloadLayout"
    cell: str


class UpdateProgressMessage(pyd.BaseModel):
    """A message to vscode to update progress status."""

    what: Literal["updateProgress"] = "updateProgress"
    index: int
    total: int
    message: str
    messageType: Literal["info", "success", "error", "warning"] = "info"  # noqa: N815


Message: TypeAlias = (
    ShowMessage
    | ErrorMessage
    | RefreshTreesMessage
    | ReloadLayoutMessage
    | ShowGdsMessage
    | RestartServerMessage
    | UpdateProgressMessage
)


def _default_pdk_name() -> str:
    return gfp_settings.get_settings().pdk.name


def _default_wls() -> gfp_settings.Linspace | gfp_settings.Arange:
    return gfp_settings.get_settings().sim.wls


class SimulationConfig(pyd.BaseModel):
    """Data model for simulation configuration."""

    pdk: str = pyd.Field(default_factory=_default_pdk_name)
    wls: gfp_settings.Linspace | gfp_settings.Arange = pyd.Field(
        default_factory=_default_wls
    )
    op: str = "none"
    port_in: str = ""
    settings: dict[str, Any] = pyd.Field(default_factory=dict)


def ensure_recursive_netlist(obj: Any) -> dict:  # noqa: C901
    """Ensure that a given object is a recursive netlist."""
    if isinstance(obj, Path):
        obj = str(obj)

    if isinstance(obj, str):
        gfp_shared.activate_pdk_by_name(gfp_settings.get_settings().pdk.name)
        if "\n" in obj or obj.endswith(".pic.yml"):
            c = from_yaml(obj)
        else:
            c = gfp_shared.build_component_with_inserted_defaults(obj)
        obj = c.get_netlist(recursive=True)

    if hasattr(obj, "model_dump"):
        obj = obj.model_dump()

    if isinstance(obj, dict) and "instances" in obj:
        # when a flat netlist is provided, assume we're doing
        # a logical simulation (not from layout if possible):
        obj = deepcopy(obj)
        pdk = gfp_shared.activate_pdk_by_name(gfp_settings.get_settings().pdk.name)
        project_dir = gfp_project.find_docode_project_dir()
        pics_dir = project_dir / gfp_settings.get_settings().name
        yaml_paths = {
            gfp_shared.get_yaml_cell_name(p): Path(p).resolve()
            for p in gfp_shared.get_yaml_paths(str(pics_dir))
        }
        recnet = {}
        for instance_name, instance in obj["instances"].items():
            if isinstance(instance, str):
                obj["instances"][instance_name] = instance = {"component": instance}
            if instance["component"] in pdk.models:
                continue
            settings = cast(dict[str, Any], instance.get("settings", {}))
            if not settings and instance["component"] in yaml_paths:
                recnet[instance["component"]] = yaml.safe_load(
                    yaml_paths[instance["component"]].read_text()
                )
            else:
                c = pdk.get_component(
                    instance["component"],
                    settings=settings,
                )
                c_recnet = c.get_netlist(recursive=True)
                obj["instances"][instance_name] = instance = {
                    "component": next(iter(c_recnet))
                }
                recnet.update(c_recnet)

        obj = {"top_level": obj, **recnet}

    if not isinstance(obj, dict):
        msg = f"Can't validate obj {obj} into RecursiveNetlist"
        raise TypeError(msg)

    return obj


class SimulationData(pyd.BaseModel):
    """Data model for simulation."""

    netlist: Annotated[dict, pyd.BeforeValidator(ensure_recursive_netlist)]
    config: SimulationConfig = pyd.Field(default_factory=SimulationConfig)


class DoItForMe(pyd.BaseModel):
    """DoItForMe Data."""

    prompt: str = ""
    initial_circuit: str = ""
    url: str = ""


class Result(pyd.BaseModel):
    """Result class containing logs and errors to be returned."""

    log: list[str] = pyd.Field(default_factory=list)
    errors: list[str] = pyd.Field(default_factory=list)


class User(pyd.BaseModel):
    """User class containing user information from GDSFactory+."""

    user_name: str
    email: str
    organization_name: str | None
    organization_id: str | None
    pdks: list[str] | None
    is_superuser: bool
