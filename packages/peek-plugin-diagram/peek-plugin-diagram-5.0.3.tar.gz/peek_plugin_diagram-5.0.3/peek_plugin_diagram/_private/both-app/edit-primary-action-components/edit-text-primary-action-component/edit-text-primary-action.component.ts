import { Component, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { ContextMenuPopupI } from "../../services/context-menu.service";
import { DispText, DispTextT } from "../../canvas-shapes/DispText";
import { DispBaseT, DispType } from "../../canvas-shapes/DispBasePartial";
import { DispBase } from "../../canvas-shapes/DispBase";
import {
    DispCurvedText,
    DispCurvedTextT,
} from "../../canvas-shapes/DispCurvedText";

@Component({
    selector: "pl-diagram-edit-text-primary-action",
    templateUrl: "edit-text-primary-action.component.html",
    styleUrls: ["edit-text-primary-action.component.scss"],
})
export class EditTextPrimaryActionComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    disp: DispBaseT | null = null;
    updateCallback: (() => void) | null = null;
    finishCallback: (() => void) | null = null;
    modalStyle = {};
    showModal = false;

    constructor() {
        super();
    }

    override ngOnInit() {}

    // --------------------
    //

    get text(): string {
        if (!this.disp) {
            return "";
        }

        if (DispBase.typeOf(this.disp) == DispType.curvedText) {
            return DispCurvedText.text(this.disp as any as DispCurvedTextT);
        }

        if (DispBase.typeOf(this.disp) == DispType.text) {
            return DispText.text(this.disp as any as DispTextT);
        }

        throw new Error(`Unhandled Type ${DispBase.typeOf(this.disp)}`);
    }

    set text(value: string) {
        if (!this.disp) {
            return;
        }

        if (DispBase.typeOf(this.disp) == DispType.curvedText) {
            DispCurvedText.setText(this.disp as any as DispCurvedTextT, value);
        } else if (DispBase.typeOf(this.disp) == DispType.text) {
            DispText.setText(this.disp as any as DispTextT, value);
        } else {
            throw new Error(`Unhandled Type ${DispBase.typeOf(this.disp)}`);
        }
        this.updateCallback?.();
    }

    open(
        disp,
        event: ContextMenuPopupI,
        finishCallback: () => void,
        updateCallback: () => void,
    ) {
        this.updateCallback = updateCallback;
        this.finishCallback = finishCallback;
        this.disp = disp;
        this.modalStyle = {
            top: `${event.y}px`,
            left: `${event.x}px`,
            margin: "20px",
            width: "300px",
        };
        this.showModal = true;
    }

    close() {
        this.finishCallback?.();

        this.showModal = false;
        this.disp = null;
        this.updateCallback = null;
        this.finishCallback = null;
    }
}
