// Prevent the browser from handling drag-and-drop default behavior
document.addEventListener("dragover", (event) => {
  event.preventDefault();
  event.stopPropagation();
});

document.addEventListener("drop", async (event) => {
  event.preventDefault();
  event.stopPropagation();

  const _items = event.dataTransfer.items;
  let x = event.clientX;
  let y = event.clientY;

  for (const item of _items) {
    if (
      item.kind === "string" &&
      item.type === "application/vnd.code.tree.picstree"
    ) {
      handleTreeItem(item, x, y);
      break;
    }
    if (
      item.kind === "string" &&
      item.type === "application/vnd.code.tree.pdktree"
    ) {
      handleTreeItem(item, x, y);
      break;
    }
    if (item.kind === "string" && item.type === "text/plain") {
      handlePlainTextItem(item, x, y);
      break;
    }
  }
});

function handleTreeItem(item, x, y) {
  return item.getAsString((content) => {
    let obj = JSON.parse(content);
    let handles = obj["itemHandles"];
    if (handles && handles.length > 0) {
      var handle = handles[0].split(":")[1].split("/")[0];
      window.wasmBindings.receive_dropped_component_name(handle, x, y);
    }
  });
}

function handlePlainTextItem(item, x, y) {
  return item.getAsString((content) => {
    let fn = baseName(content);
    let handle;
    if (fn.endsWith(".gds") || fn.endsWith(".oas")) {
      handle = fn.slice(0, -4);
    } else if (fn.endsWith(".pic.yml")) {
      handle = fn.slice(0, -8);
    } else {
      return;
    }
    window.wasmBindings.receive_dropped_component_name(handle, x, y);
  });
}

function reloadNetlist() {
  window.wasmBindings.reload_netlist();
}

function baseName(path) {
  return path.split(/[/\\]/).pop();
}

async function fetchString(url) {
  const response = await fetch(url);
  return await response.text();
}

async function postString(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "text/plain",
    },
    body: body,
  });
  return await response.text();
}

function sleep(s) {
  return new Promise((resolve) => setTimeout(resolve, s * 1000));
}

window.addEventListener("message", (event) => {
  console.log("Received message from parent:", event.data);
  const msg = JSON.parse(event.data);
  console.log("Parsed message:", JSON.stringify(msg));
  if (Object.entries(msg).length < 1) {
    return;
  }
  let command = Object.keys(msg)[0];
  if (command) {
    switch (command) {
      case "reload":
        onReload(msg[command]);
        break;
      case "active":
        onActive(msg[command]);
        break;
      case "placement":
        onPlacement(msg[command]);
        break;
      case "setBuildStatus":
        onSetBuildStatus(msg[command]);
      default:
        console.log("Unknown command: " + command);
        break;
    }
  }
});

function onActive(value) {
  if (value) {
    window.wasmBindings.set_active();
  } else {
    window.wasmBindings.set_inactive();
  }
}

function onReload(value) {
  if (value) {
    reloadNetlist();
  }
}

function onSetBuildStatus(status) {
  window.wasmBindings.set_build_status(status);
}

function onPlacement(value) {
  window.wasmBindings.set_placement(
    value.name,
    value.dx,
    value.dy,
    value.rotation,
    value.mirror,
  );
}
