import { DialogComponent } from "@components/common/dialogs/dialog-component";
import "@components/item/item-editor";
import { SnackbarComponent } from "@components/common/snackbar/snackbar";

export class EditItemDialog extends DialogComponent {
    private editor!: HTMLElement;
    private itemData: any;

    constructor(itemData: any) {
        super({
            id: "edit-item-dialog",
            title: "Edit Item",
            bodyContent: `<item-editor></item-editor>`
        });

        this.itemData = itemData;
        this.init();
    }

    init() {
        window.addEventListener("resize", this.handleResize);
        this.handleResize();

        // ensure DOM is ready
        setTimeout(() => {
            this.editor = document.querySelector("item-editor")!;

            // load existing values
            (this.editor as any).load(this.itemData);

            // listen for save click from editor
            this.editor.addEventListener("save", async (e: any) => {
                await this.handleSave(e.detail);
            });
        });
    }

    async handleSave(formData: FormData) {
        try {
            const colony = document.body.getAttribute("data-colony");

            // MUST include ID for update
            formData.append("id", String(this.itemData.id));

            const res = await fetch(`/api/colony/${colony}/items/update`, {
                method: "POST",
                body: formData,
            });

            const json = await res.json();

            if (!json.success) {
                SnackbarComponent.error(json.error || "Could not update item");
                return;
            }

            SnackbarComponent.success("Item updated successfully!");
            this.close();
            window.location.reload();

        } catch (err) {
            SnackbarComponent.error("Error updating item");
            console.error(err);
        }
    }
}