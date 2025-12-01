import { AddItemDialog } from "@components/common/dialogs/add-item-dialog";
import { ItemEditor } from "./item-editor";

export class ItemElementComponent extends HTMLElement {
    connectedCallback() {
        const name = this.getAttribute("data-name") || "";
        const description = this.getAttribute("data-description") || "";
        const thumbnail = this.getAttribute("data-thumbnail");
        const points = this.getAttribute("data-points");
        const category = this.getAttribute("data-category") || "";
        const tags = JSON.parse(this.getAttribute("data-tags") || "[]");
        const isActive = this.getAttribute("data-active") === "true";

        const thumbUrl = thumbnail ? `/uploaded_thumbnails/${thumbnail}` : "/static/images/no-thumbnail.png";
        this.classList.add("s12", "m6", "l4");
        this.innerHTML = `
            <article class="round border">
                <img src="${thumbUrl}" class="responsive small round bottom-margin" />
                <div class="padding">
                    <h5>${name}</h5>
                    <p class="tiny-text">${description}</p>

                    <nav class="row middle">
                        <span class="chip">
                            <i>star</i><span>${points} pts</span>
                        </span>

                        ${category ? `<span class="chip"><i>category</i>${category}</span>` : ""}
                        ${tags.map((t: string) => `<span class="chip tiny">${t}</span>`).join("")}
                    </nav>

                    ${!isActive ? `<p class="tiny-text red-text"><i>warning</i> Inactive</p>` : ""}

                    <nav class="right-align top-margin">
                        <button class="chip edit-btn">
                            <i>edit</i>
                            <span>Edit</span>
                        </button>
                    </nav>
                </div>
            </article>
            `;
        this.querySelector(".edit-btn")?.addEventListener("click", () => {
            new AddItemDialog();
        });
    }
}

customElements.define("item-element", ItemElementComponent);
