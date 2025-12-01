import "beercss"
import "material-dynamic-colors"
import "@utils/theme"
import "@components/common/footer/footer-component"
import "@components/common/button/help-button"
import "@components/common/button/share-button"
import "@components/item/item-element";
import "@components/colony/colony-items";

document.addEventListener("DOMContentLoaded", () => {
    const body = document.querySelector("body")
    if (body) {
        const colonyTheme = body.getAttribute("data-theme")
        if (colonyTheme) {
            ui("theme", colonyTheme);
        }
    }
})