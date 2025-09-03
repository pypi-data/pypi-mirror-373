const toggleVisibility = (node) => {
    for (const item of node.getElementsByClassName("more")) {
        item.classList.toggle("d-none")
    }
}

const createIcon = () => {
    const node = document.createElement("span")
    const icon = document.createElement("img")
    icon.src = "/static/admin/img/icon-viewlink.svg"
    icon.title = "Toggle more/less."
    node.appendChild(icon)
    node.style.cursor = "pointer"
    node.classList.add("item-after")
    return node
}

document.addEventListener('DOMContentLoaded', () => {
    for (const data of document.getElementsByClassName("aldryn-forms-data")) {
        const icon = createIcon()
        data.prepend(icon)
        icon.addEventListener("click", (event) => {
            toggleVisibility(event.target.closest(".aldryn-forms-data"))
        })
    }

    const column = document.querySelector("#result_list th.column-display_data div.text")
    if (column) {
        const icon = createIcon()
        icon.addEventListener("click", () => {
            for (const item of document.getElementsByClassName("aldryn-forms-data")) {
                toggleVisibility(item)
            }
        })
        column.appendChild(icon)
    }
})
