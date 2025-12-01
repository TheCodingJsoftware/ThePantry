import { DialogComponent } from "@components/common/dialogs/dialog-component";
import "@components/item/item-editor";
import { SnackbarComponent } from "@components/common/snackbar/snackbar";

export class AddItemDialog extends DialogComponent {
    private editor!: HTMLElement;

    constructor() {
        super({
            id: "add-item-dialog",
            title: "Add Item",
            bodyContent: `<item-editor></item-editor>`,
        });

        this.init();
    }

    init() {
        window.addEventListener("resize", this.handleResize);
        this.handleResize();

        // Wait for dialog DOM to exist
        setTimeout(() => {
            this.editor = document.querySelector("item-editor")!;

            // Listen for the "save" event that item-editor dispatches
            this.editor.addEventListener("save", async (e: any) => {
                await this.handleSave(e.detail);
            });
        });
    }

    async handleSave(formData: FormData) {
        try {
            const colony = document.body.getAttribute("data-colony");

            const res = await fetch(`/api/colony/${colony}/items/add`, {
                method: "POST",
                body: formData,
            });

            const json = await res.json();

            if (!json.success) {
                SnackbarComponent.error(json.error || "Could not save item");
                return;
            }

            SnackbarComponent.success("Item added successfully!");

            // Close dialog
            this.close();

            // Reload list
            window.location.reload();

        } catch (err: any) {
            SnackbarComponent.error("Error saving item");
            console.error(err);
        }
    }
}
