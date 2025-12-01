import { AddItemDialog } from "@components/common/dialogs/add-item-dialog";

export class AddItemButton extends HTMLButtonElement {
    constructor() {
        super();

        this.innerHTML = `
            <i>add</i>
            <span class="l m">Add New Item</span>
        `;
    }

    connectedCallback() {
        this.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            new AddItemDialog();
        });
    }
}

customElements.define("add-item-button", AddItemButton, { extends: "button" });
