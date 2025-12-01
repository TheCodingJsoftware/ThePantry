export class ColonyItemsComponent extends HTMLElement {
    constructor() {
        super();
        this.innerHTML = `
            <section id="items-list" class="grid">
                <!-- items get injected here -->
            </section>
        `;
    }

    connectedCallback() {
        this.loadItems();
    }

    async loadItems() {
        const colony = document.body.getAttribute("data-colony");

        const res = await fetch(`/api/colony/${colony}/items`);
        const json = await res.json();

        if (!json.success) {
            console.error("Failed to load colony items:", json.error);
            return;
        }

        const container = this.querySelector("#items-list")!;

        container.innerHTML = ""; // Clear container

        json.items.forEach((item: any) => {
            const el = document.createElement("item-element");
            el.setAttribute("data-id", item.id);
            el.setAttribute("data-name", item.name);
            el.setAttribute("data-description", item.description || "");
            el.setAttribute("data-thumbnail", item.thumbnail_path || "");
            el.setAttribute("data-points", item.points_per_item);
            el.setAttribute("data-category", item.category || "");
            el.setAttribute("data-tags", JSON.stringify(item.tags || []));
            el.setAttribute("data-active", item.is_active);

            container.appendChild(el);
        });
    }
}

customElements.define("colony-items", ColonyItemsComponent);
