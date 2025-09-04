"""GDS Viewer Additions to KWeb/DoWeb."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import doweb.api.viewer as doweb_viewer
from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from gdsfactoryplus.core.pdk import get_pdk
from gdsfactoryplus.core.shared import merge_rdb_strings

from .app import PDK, PROJECT_DIR, app, logger


@app.get("/view2")
async def view2(
    request: Request,
    file: str,
    cell: str = "",
    rdb: str = "",
    theme: Literal["light", "dark"] = "dark",
    *,
    regen_lyp: bool = False,
) -> HTMLResponse:
    """Alternative view specifically for GDSFactory+."""
    if PROJECT_DIR is None:
        msg = "GDSFactory+ server was not started correctly."
        raise ValueError(msg)

    gds_path = Path(file).resolve()

    lyrdb_dir = PROJECT_DIR / "build" / "lyrdb"
    temp_rdb = False
    prdb = None
    if rdb:
        rdbs = [Path(p).resolve() for p in rdb.split(",")]
        logger.info(rdbs)
        if len(rdbs) == 1 and rdbs[0].is_relative_to(lyrdb_dir / "temp"):
            prdb = rdbs[0]
            temp_rdb = True  # noqa: F841
        else:
            prdb = lyrdb_dir / rdbs[0].name
            xmls = [Path(xml).read_text() for xml in rdbs]
            xml = merge_rdb_strings(*xmls)
            prdb.write_text(xml)

    layer_props = PROJECT_DIR / "build" / "lyp" / f"{PDK}.lyp"
    if regen_lyp or not layer_props.is_file():
        _pdk = get_pdk()
        layer_views = _pdk.layer_views
        if layer_views is not None:
            if isinstance(layer_views, str | Path):
                layer_props = str(Path(layer_views).resolve())
            else:
                layer_views.to_lyp(filepath=layer_props)

    try:
        fv = doweb_viewer.FileView(
            file=gds_path,
            cell=cell or None,
            layer_props=str(layer_props),
            rdb=None if not rdb else str(prdb),
        )
        resp = await doweb_viewer.file_view_static(request, fv)
    except HTTPException:
        color = "#f5f5f5" if theme == "light" else "#121317"
        return HTMLResponse(f'<body style="background-color: {color}"></body>')
    body = resp.body.decode()  # type: ignore[reportAttributeAccessIssue]
    body = _modify_body(body, theme, str(gds_path), temp_rdb=False)  # temp_rdb)
    return HTMLResponse(body)


def _modify_body(body: str, theme: str, file: str, *, temp_rdb: bool = False) -> str:
    if theme == "light":
        body = body.replace('data-bs-theme="dark"', 'data-bs-theme="light"')
    body = body.replace(
        "</head>",
        """<style>
     [data-bs-theme=light] {
       --bs-body-bg: #f5f5f5;
     }
     [data-bs-theme=dark] {
       --bs-body-bg: #121317;
     }
   </style>
   </head>""",
    )
    body = body.replace(
        "</body>",
        """<script>
            const tempRdb = %temp_rdb%;
            window.onload = () => {
            setTimeout(()=>{
              let categoryOptionsEl = document.getElementById("rdbCategoryOptions");
              let cellOptionsEl = document.getElementById("rdbCellOptions");
              let rdbItemsEl = document.getElementById("rdbItems");
              if (tempRdb) {
                document.getElementById("rdb-tab").click();
                 for (o of categoryOptionsEl.options){
                   categoryOptionsEl.value=o.value
                 }
                 let ev = new Event("change");
                 console.log("value", categoryOptionsEl.value);
                 categoryOptionsEl.dispatchEvent(ev);
                 for (o of cellOptionsEl.options){
                   cellOptionsEl.value=o.value
                 }
                 cellOptionsEl.dispatchEvent(ev);
                 setTimeout(() => {
                   for (o of rdbItemsEl.options) {
                     o.selected = true;
                   }
                   requestItemDrawings();
                 }, 200);
              }
              }, 500)
            }
            window.addEventListener("message", (event) => {
              const message = JSON.parse(event.data);
              let categoryOptionsEl = document.getElementById("rdbCategoryOptions");
              let cellOptionsEl = document.getElementById("rdbCellOptions");
              let rdbItemsEl = document.getElementById("rdbItems");

              // refresh is equivalent to a browser refresh.
              let refresh = message.refresh;
              if (refresh) {
                window.location.reload()
                return
              }

              // reload just reloads the gds without refreshing the page.
              let reload = message.reload;
              if (reload) {
                let previousMode = currentMode;
                document.getElementById("reload").click();
                let row = document.getElementById("mode-row");
                if (row) {
                  for (let child of row.children) {
                      if (child.checked) {
                          child.click();
                          break
                      }
                  }
                }
                if (selectTool) {
                  selectTool(previousMode);
                }
                return
              }

              let category = message.category;
              let cell = message.cell;
              let itemIdxs = message.itemIdxs;

              console.log(`CATEGORY=${category}`);
              console.log(`CELL=${cell}`);
              console.log(`itemIdxs=${itemIdxs}`);

              document.getElementById("rdb-tab").click();
              //const event = new Event('change');
              let categoryOptions = Array.from(categoryOptionsEl.children)
                .map((c)=>[c.innerHTML, c.value])
                .reduce((acc, [key, value]) => {acc[key] = value; return acc;}, {});
              let cellOptions = Array.from(cellOptionsEl.children)
                .map((c)=>[c.innerHTML, c.value])
                .reduce((acc, [key, value]) => {acc[key] = value; return acc;}, {});
              console.log(categoryOptions)
              console.log(cellOptions)
              let cellIndex = cellOptions[cell];
              let categoryIndex = categoryOptions[category];
              console.log(`cellIndex: ${cellIndex}`);
              console.log(`categoryIndex: ${categoryIndex}`);
              categoryOptionsEl.value = categoryIndex;
              cellOptionsEl.value = cellIndex;
              let ev = new Event("change");
              categoryOptionsEl.dispatchEvent(ev);
              cellOptionsEl.dispatchEvent(ev);
              setTimeout(() => {
                for (itemIndex of itemIdxs) {
                  let idx = `${itemIndex}`;
                  let o = rdbItemsEl.options[idx];
                  if (o) {
                      o.selected = true;
                  }
                  requestItemDrawings();
                }
              }, 200);
            });
        </script>
        </body>
        """.replace("%path%", file.replace("\\", "\\\\")).replace(
            "%temp_rdb%", str(temp_rdb).lower()
        ),
    )
    return body.replace(" shadow ", " shadow-none ")
