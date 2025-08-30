import { Component, ViewChild } from "@angular/core";
import { EditPrimaryActionHandlerFactory } from "../../edit-priamry-action-handlers/EditPrimaryActionHandlerFactory";
import { EditPrimaryActionHandlerArgsI } from "../../edit-priamry-action-handlers/EditPrimaryActionHandlerArgsI";
import { EditTextPrimaryActionComponent } from "../edit-text-primary-action-component/edit-text-primary-action.component";

@Component({
    selector: "pl-diagram-edit-primary-action",
    templateUrl: "edit-primary-action.component.html",
    styleUrls: ["edit-primary-action.component.scss"],
})
export class EditPrimaryActionComponent {
    @ViewChild("textActionComponent", { static: true })
    private textActionComponent: EditTextPrimaryActionComponent;

    constructor() {}

    createFactory(): EditPrimaryActionHandlerFactory {
        const args: EditPrimaryActionHandlerArgsI = {
            textActionComponent: this.textActionComponent,
        };
        return new EditPrimaryActionHandlerFactory(args);
    }
}
