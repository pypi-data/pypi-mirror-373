import { Component, Input } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";

@Component({
    selector: "pl-diagram-edit-props-livedb",
    templateUrl: "edit-props-livedb.component.html",
    styleUrls: ["edit-props-livedb.component.scss"],
})
export class EditPropsLivedbComponent extends NgLifeCycleEvents {
    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;

    constructor() {
        super();
    }
}
