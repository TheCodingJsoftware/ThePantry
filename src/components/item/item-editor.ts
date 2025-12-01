import { SnackbarComponent } from "@components/common/snackbar/snackbar";

export class ItemEditor extends HTMLElement {
    private itemId: number | null = null;

    constructor() {
        super();

        this.innerHTML = `
        <div class="grid">
            <!-- ITEM NAME -->
            <div class="s12 m6 l8 round field label border bottom-margin">
                <input type="text" id="name">
                <label>Item Name</label>
            </div>

            <!-- POINTS -->
            <div class="s12 m6 l4 round field label border bottom-margin">
                <input type="number" id="points_per_item" min="1">
                <label>Points Per Item</label>
            </div>

            <!-- DESCRIPTION -->
            <div class="s12 field textarea label border bottom-margin">
                <textarea id="description" rows="3"></textarea>
                <label>Description</label>
            </div>

            <!-- THUMBNAIL UPLOAD -->
            <label class="s12 small-text">Thumbnail</label>
            <div class="s12 bottom-margin">
                <input type="file" accept="image/*" id="thumbnail" style="display:none;">
                <button class="chip" id="thumbnail-btn">
                    <i>upload</i><span>Upload Thumbnail</span>
                </button>
                <span id="thumbnail-name" class="tiny-text left-padding"></span>
            </div>

            <!-- WEBSITE URL -->
            <div class="s12 round field label border bottom-margin">
                <input type="text" id="website_url">
                <label>Website URL</label>
            </div>

            <!-- CATEGORY -->
            <div class="s12 round field label border bottom-margin">
                <input type="text" id="category">
                <label>Category</label>
            </div>

            <!-- TAGS (comma-separated) -->
            <div class="s12 field label border bottom-margin">
                <input type="text" id="tags">
                <label>Tags (comma separated)</label>
            </div>

            <!-- ACTIVE -->
            <label class="s12 checkbox middle center bottom-margin">
                <input type="checkbox" id="is_active" checked>
                <span class="left-padding">Is Active</span>
            </label>

            <!-- MAX ALLOWED -->
            <div class="s12 m6 l6 round field label border bottom-margin">
                <input type="number" id="max_allowed" min="0" value="0">
                <label>Max Allowed</label>
                <span class="helper">0 = no limit</span>
            </div>

            <!-- DEFAULT QUANTITY -->
            <div class="s12 m6 l6 round field label border bottom-margin">
                <input type="number" id="default_quantity" min="1" value="1">
                <label>Default Quantity</label>
            </div>

            <!-- SAVE BUTTON -->
            <nav class="s12 right-align">
                <button id="save-btn">
                    <i>save</i>
                    <span>Save Item</span>
                </button>
            </nav>

        </article>
        `;
    }

    connectedCallback() {
        this.querySelector("#image-btn")?.addEventListener("click", () =>
            this.querySelector<HTMLInputElement>("#image")?.click()
        );
        this.querySelector("#thumbnail-btn")?.addEventListener("click", () =>
            this.querySelector<HTMLInputElement>("#thumbnail")?.click()
        );

        this.querySelector("#image")?.addEventListener("change", (e: any) => {
            const file = e.target.files?.[0];
            if (file) this.querySelector("#image-name")!.textContent = file.name;
        });

        this.querySelector("#thumbnail")?.addEventListener("change", (e: any) => {
            const file = e.target.files?.[0];
            if (file) this.querySelector("#thumbnail-name")!.textContent = file.name;
        });

        this.querySelector("#save-btn")!.addEventListener("click", () => {
            this.dispatchEvent(new CustomEvent("save", {
                detail: this.getFormData()
            }));
        });
    }

    /**
     * Populate the form with existing row data
     */
    load(data: any) {
        this.itemId = data.id ?? null;

        (this.querySelector("#name") as HTMLInputElement).value = data.name ?? "";
        (this.querySelector("#description") as HTMLTextAreaElement).value = data.description ?? "";
        (this.querySelector("#points_per_item") as HTMLInputElement).value = data.points_per_item ?? 1;

        (this.querySelector("#website_url") as HTMLInputElement).value = data.website_url ?? "";
        (this.querySelector("#category") as HTMLInputElement).value = data.category ?? "";
        (this.querySelector("#tags") as HTMLInputElement).value = (data.tags ?? []).join(", ");

        (this.querySelector("#is_active") as HTMLInputElement).checked = data.is_active ?? true;

        (this.querySelector("#max_allowed") as HTMLInputElement).value =
            data.max_allowed !== null && data.max_allowed !== undefined ? data.max_allowed : "";

        (this.querySelector("#default_quantity") as HTMLInputElement).value =
            data.default_quantity ?? 1;

        // Media filenames if already stored
        this.querySelector("#image-name")!.textContent = data.image_path ?? "";
        this.querySelector("#thumbnail-name")!.textContent = data.thumbnail_path ?? "";
    }

    /**
     * Collects into FormData ready for POST
     */
    getFormData(): FormData {
        const form = new FormData();

        if (this.itemId !== null) form.append("id", String(this.itemId));

        form.append("name", this.value("#name"));
        form.append("description", this.value("#description"));
        form.append("points_per_item", this.value("#points_per_item"));
        form.append("website_url", this.value("#website_url"));
        form.append("category", this.value("#category"));
        form.append("tags", this.value("#tags"));

        form.append("is_active", (this.querySelector("#is_active") as HTMLInputElement).checked ? "true" : "false");
        form.append("max_allowed", this.value("#max_allowed") || "0");
        form.append("default_quantity", this.value("#default_quantity"));

        const thumb = (this.querySelector("#thumbnail") as HTMLInputElement).files?.[0];
        if (thumb) form.append("thumbnail", thumb);

        return form;
    }

    private value(sel: string): string {
        return (this.querySelector(sel) as HTMLInputElement).value.trim();
    }
}

customElements.define("item-editor", ItemEditor);
