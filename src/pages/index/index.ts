import "beercss"
import "material-dynamic-colors"
import "@utils/theme"
import "@components/common/footer/footer-component"
import { DEFAULT_COLOR } from "@utils/colors"

document.addEventListener("DOMContentLoaded", () => {
    ui("theme", DEFAULT_COLOR);
});