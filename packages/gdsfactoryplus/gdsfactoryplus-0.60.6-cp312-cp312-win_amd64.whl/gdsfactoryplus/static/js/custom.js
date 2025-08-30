function onChangeKey(key) {
    let wrapper = document.getElementById("edit_val_wrapper");
    for (let child of wrapper.children) {
        child.style.display = "none";
    }
    let el = document.getElementById("edit_val-" + key);
    el.style.display = "inline";
}

function goto(id) {
    let el = document.getElementById(id);
    el.click();
}

function cancel(el) {
    el.remove();
}

document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        let el = document.getElementById("accept");
        if (el) {
            el.click();
        }
    }
});
