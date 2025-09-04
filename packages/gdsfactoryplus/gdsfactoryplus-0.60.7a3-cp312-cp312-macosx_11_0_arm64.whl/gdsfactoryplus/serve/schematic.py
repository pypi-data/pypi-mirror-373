"""Schematic editor routes."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from typing import Annotated, Any

import gdsfactory as gf
import orjson
import yaml
from fastapi import Body, HTTPException
from fastapi.responses import (
    JSONResponse,
    PlainTextResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles
from natsort import natsorted

from gdsfactoryplus.core.generate_svg import get_svg
from gdsfactoryplus.core.pdk import find_source_path, get_pdk
from gdsfactoryplus.core.schema import get_ports
from gdsfactoryplus.core.shared import extract_function_arguments

from .app import PROJECT_DIR, app, logger

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


@app.get("/assets/netlists/{path:path}.json")
def get_netlist(path: str) -> JSONResponse:
    """Get the netlist and schematic from file."""
    netlist_path = Path(f"{path}.pic.yml").resolve()
    schematic_path = Path(f"{path}.scm.yml").resolve()
    if netlist_path.is_file():
        with netlist_path.open("r") as yamlp:
            netlist = yaml.safe_load(yamlp)
    else:
        netlist = {}
    if not isinstance(netlist, dict):
        netlist = {}
    if schematic_path.is_file():
        with schematic_path.open("r") as yamlp:
            schematic = yaml.safe_load(yamlp)
    else:
        schematic = {}
    if not isinstance(schematic, dict):
        schematic = {}
    return JSONResponse(
        {
            "netlist": netlist,
            "schematic": schematic,
        }
    )


@app.post("/assets/netlists/{path:path}.json")
def post_netlist(body: Annotated[str, Body()], *, path: str) -> PlainTextResponse:
    """Post a netlist to save to a file."""
    try:
        netlist_and_schematic = orjson.loads(body)
    except Exception:  # noqa: BLE001
        netlist_and_schematic = {}
    if not isinstance(netlist_and_schematic, dict):
        netlist_and_schematic = {}
    if not netlist_and_schematic:
        return PlainTextResponse("Refused to save empty netlist.", status_code=422)
    netlist = netlist_and_schematic.get("netlist", {})
    schematic = netlist_and_schematic.get("schematic", {})
    netlist_path = Path(f"{path}.pic.yml").resolve()
    schematic_path = Path(f"{path}.scm.yml").resolve()
    netlist_path.parent.mkdir(parents=True, exist_ok=True)
    schema_dir = PROJECT_DIR / "build" / "schemas"
    schema_path = (schema_dir / Path(f"{path}.json").resolve().name).relative_to(
        schematic_path.parent, walk_up=True
    )
    with schematic_path.open("w") as file:
        yaml.safe_dump(schematic, file, sort_keys=False)
    yaml_str = yaml.safe_dump(netlist, sort_keys=False)
    yaml_str = f"# yaml-language-server: $schema={schema_path}\n{yaml_str}".strip()
    with netlist_path.open("r") as file:
        present_yaml_str = file.read().strip()
    if yaml_str != present_yaml_str:
        with netlist_path.open("w") as file:
            file.write(yaml_str)
    return PlainTextResponse(f"netlist saved to {netlist_path}.")


@app.get("/assets/settings/{component}.json")
def settings(component: str) -> dict:  # noqa: C901
    """Get component settings."""
    pdk = get_pdk()
    refs = {}
    component_settings = {}
    component_settings[component] = {}
    cell = pdk.cells.get(component)

    try:
        cell = pdk.cells[component]
        types = _get_allowed_instance_settings(cell)
        defaults = extract_function_arguments(cell)
    except KeyError:
        types, defaults = {}, {}

    for key, tp in types.items():
        component_settings[component][key] = {
            "default": None,
            "type": tp,
        }
        if key in defaults:
            component_settings[component][key]["default"] = defaults[key]
            if defaults[key] in pdk.cells:
                if "@component" not in refs:
                    refs["@component"] = list(pdk.cells)
                component_settings[component][key]["type"] = "@component"
            if defaults[key] in pdk.cross_sections:
                if "@cross_section" not in refs:
                    refs["@cross_section"] = [
                        xs for xs in pdk.cross_sections if xs != "cross_section"
                    ]
                component_settings[component][key]["type"] = "@cross_section"

        type_ = component_settings[component][key]["type"]
        if isinstance(type_, list) and len(type_) > 1:
            if type_[0] in pdk.cells:  # TODO: improve this heuristic.
                if "@component" not in refs:
                    refs["@component"] = list(pdk.cells)
                component_settings[component][key]["type"] = "@component"
            else:
                if f"@{key}" not in refs:
                    refs["@key"] = type_
                component_settings[component][key]["type"] = f"@{key}"

    return component_settings[component]


@app.get("/assets/ports/{component}.json")
def ports(component: str) -> dict:
    """Get component ports."""
    return _get_ports(component)


@app.get("/assets/ports-extended/{component}.json")
def ports_extended(component: str) -> dict:
    """Get all ports."""
    pdk = get_pdk()
    ports = _get_ports(component)
    ret = {
        k: {"orientation": v, "port_type": "optical", "index": float(i)}
        for i, (k, v) in enumerate(ports.items())
    }
    cell_func = pdk.cells.get(component)
    if cell_func is not None:
        try:
            cell = cell_func()
            for port in cell.ports:
                if port.name not in ret:
                    ret[port.name] = {
                        "orientation": "w",
                        "port_type": "optical",
                        "index": 0.0,
                    }
                else:
                    ret[port.name]["port_type"] = port.port_type
                    if ret[port.name]["orientation"] in ["w", "e"]:
                        ret[port.name]["index"] = port.center[1]
                    else:
                        ret[port.name]["index"] = port.center[0]
        except Exception as e:  # noqa: BLE001
            logger.warning(str(e))
    return ret


@app.get("/assets/routing-strategies.json")
def routing_strategies() -> dict:
    """Get routing strategies."""
    pdk = get_pdk()
    refs = {}
    ret = {}
    for k, v in (pdk.routing_strategies or {}).items():
        if _is_bundle(v):
            args = _get_types_and_defaults_for_routing(v)
            refs.update(args.pop("@refs"))
            ret[k] = args
    return {"strategies": ret, "refs": refs}


@app.get("/assets/svg/{component}.svg")
def svg(component: str, width: int = 80, height: int = 80) -> Response:
    """Get component svg."""
    return _svg(component, width, height, "light")


@app.get("/assets/svg-dark/{component}.svg")
def svg_dark(component: str, width: int = 80, height: int = 80) -> Response:
    """Get component svg."""
    return _svg(component, width, height, "dark")


def _get_types_and_defaults_for_routing(func: Callable) -> dict:  # noqa: C901,PLR0912
    pdk = gf.get_active_pdk()
    defaults = extract_function_arguments(func)
    types = _get_allowed_instance_settings(func)
    refs = {}
    ret = {}
    for k in natsorted(set(types) | set(defaults)):
        default = defaults.get(k, None)
        tpe = types.get(k, None)

        if k == "waypoints":
            tpe = "Waypoints"
        elif k == "port_type":
            tpe = "@port_type"
            if "@port_type" not in refs:
                refs["@port_type"] = ["optical", "electrical"]
            default = default or "optical"
            refs["@port_type"].append(default)
        if k in ["component", "port1", "port2", "ports1", "ports2"]:
            continue

        if default is None:
            if tpe == "str":
                default = ""
            elif tpe == "bool":
                default = False
        if tpe is None:
            tpe = "str"
        elif tpe == "float | list[float]":
            tpe = "float"
        elif tpe == "Iterable":
            tpe = "list"
        elif isinstance(tpe, list) and len(tpe) > 0:
            if tpe[0] in pdk.cells:
                refs["@component"] = tpe
                tpe = "@component"
            elif tpe[0] in pdk.cross_sections:
                refs["@cross_section"] = tpe
                tpe = "@cross_section"
        elif tpe == "NoneType":
            tpe = "str"

        if isinstance(tpe, str):
            tpe = tpe.replace(" ", "").replace("|None", "").replace("None|", "").strip()
            if default is None:
                tpe = f"{tpe}?"

        ret[k] = {
            "default": default,
            "type": tpe,
        }
    if "component" in ret:
        ret = {"component": ret.pop("component"), **ret}
    if "@port_type" in refs:
        refs["@port_type"] = natsorted(set(refs["@port_type"]))
    return {**ret, "@refs": refs}


def _get_allowed_instance_settings(pcell: Callable[..., Any]) -> dict[str, Any]:
    pdk = gf.get_active_pdk()
    types = {}
    for k, p in inspect.signature(pcell).parameters.items():
        if p.annotation is inspect.Parameter.empty:
            if p.default is inspect.Parameter.empty:
                types[k] = "str"
            else:
                types[k] = getattr(p.default, "__class__", str).__name__
        else:
            types[k] = getattr(p.annotation, "__name__", str(p.annotation))
        types[k] = types[k].replace("| None", "").strip()
        if "CrossSection" in types[k]:
            types[k] = [xs for xs in pdk.cross_sections if xs != "cross_section"]
        elif "Component" in types[k]:
            types[k] = list(pdk.cells)
    types.pop("kwargs", None)
    return types


def _get_ports(component: str, **kwargs: Any) -> dict:
    pdk = get_pdk()
    path = None

    with suppress(Exception):
        path = find_source_path(component, pdk.cells[component])

    net_ports = {}
    if path and path.is_file() and (path.suffix == ".pic.yml"):
        net = yaml.safe_load(path.read_text())
        net_ports = _ports_from_netlist(net)

    if net_ports:
        return net_ports

    if not pdk.cells.get(component):
        return {}

    return get_ports(component, **kwargs)


def _ports_from_netlist(netlist: dict) -> dict:
    ports = sorted(netlist.get("ports", {}))
    w_ports = [p for p in ports if p.startswith("in")]
    e_ports = [p for p in ports if p.startswith("out")]
    n_ports = []
    s_ports = []
    o_ports = [p for p in ports if p not in w_ports and p not in w_ports]
    if len(o_ports) == 0:
        pass
    elif len(o_ports) == 1:
        w_ports.append(o_ports[0])
    elif len(o_ports) == 2:
        w_ports.append(o_ports[0])
        e_ports.append(o_ports[1])
    elif len(o_ports) == 3:
        w_ports.append(o_ports[0])
        n_ports.append(o_ports[1])
        e_ports.append(o_ports[2])
    else:
        length = len(o_ports) // 4
        w_ports.extend(o_ports[:length])
        n_ports.extend(o_ports[length : 2 * length])
        e_ports.extend(o_ports[2 * length : -length])
        s_ports.extend(o_ports[-length:])
    ports = {}
    for port in w_ports:
        ports[port] = "w"
    for port in n_ports:
        ports[port] = "n"
    for port in e_ports:
        ports[port] = "e"
    for port in s_ports:
        ports[port] = "s"
    return ports


def _is_bundle(func: Callable) -> bool:
    params = inspect.signature(func).parameters
    return "ports1" in params and "ports2" in params


def _svg(
    component: str,
    width: int = 80,
    height: int = 80,
    theme: str = "dark",
    /,
    **kwargs: Any,
) -> Response:
    ports = _get_ports(component)
    nports = len([p for p, o in ports.items() if o == "n"])
    eports = len([p for p, o in ports.items() if o == "e"])
    sports = len([p for p, o in ports.items() if o == "s"])
    wports = len([p for p, o in ports.items() if o == "w"])
    xports = max(nports, sports)
    yports = max(eports, wports)
    width = max(20 * xports, width)
    height = max(20 * yports, height)
    try:
        comp = get_pdk().get_component(component, **kwargs)
    except Exception as e:
        raise HTTPException(
            status_code=204,
            detail=f"Could not generate svg for {component}.",
        ) from e
    svg = get_svg(comp, width, height, theme=theme)
    return Response(svg, media_type="image/svg+xml")


app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
