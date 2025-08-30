import { Observable } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { EditorContextType } from "../canvas/PeekCanvasEditorProps";
import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch/BranchTuple";

@Component({
    selector: "pl-diagram-edit-props",
    templateUrl: "edit-props.component.web.html",
    styleUrls: ["edit-props.component.web.scss"],
})
export class EditPropsComponent extends NgLifeCycleEvents implements OnInit {
    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;

    currentContext: EditorContextType = EditorContextType.NONE;
    isContextShown: boolean = false;

    constructor() {
        super();
    }

    override ngOnInit() {
        this.canvasEditor.props.contextPanelObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((val: EditorContextType) => {
                this.isContextShown = val !== EditorContextType.NONE;
                this.currentContext = val;
            });
    }

    title() {
        let lookup = [];
        lookup[EditorContextType.NONE] = "No Panel";
        lookup[EditorContextType.BRANCH_PROPERTIES] = "Branch Properties";
        lookup[EditorContextType.SHAPE_PROPERTIES] = "Shape Properties";
        lookup[EditorContextType.DYNAMIC_PROPERTIES] = "Dynamic Properties";
        return lookup[this.currentContext];
    }

    modelSetKey(): string {
        if (this.canvasEditor.branchContext == null) return null;
        return this.canvasEditor.branchContext.modelSetKey;
    }

    coordSetKey(): string {
        if (this.canvasEditor.branchContext == null) return null;
        return this.canvasEditor.branchContext.coordSetKey;
    }

    globalBranchKey(): string {
        if (this.canvasEditor.branchContext == null) return null;
        return this.canvasEditor.branchContext.key;
    }

    diagramBranchTuple(): BranchTuple | null {
        if (this.canvasEditor.branchContext == null) return null;
        return this.canvasEditor.branchContext.branchTuple;
    }

    diagramBranchUpdatedObservable(): Observable<boolean> | null {
        if (this.canvasEditor.branchContext == null) return null;
        return this.canvasEditor.branchContext.branchUpdatedObservable;
    }

    closePopup(): void {
        this.canvasEditor.props.closeContext();
        this.canvasEditor.dispPropsUpdated(true);
    }

    isShowingBranchPropertiesContext(): boolean {
        return this.currentContext === EditorContextType.BRANCH_PROPERTIES;
    }

    isShowingShapePropertiesContext(): boolean {
        return this.currentContext === EditorContextType.SHAPE_PROPERTIES;
    }

    isShowingDynamicPropertiesContext(): boolean {
        return this.currentContext === EditorContextType.DYNAMIC_PROPERTIES;
    }

    isShowingGroupPtrPropertiesContext(): boolean {
        return this.currentContext === EditorContextType.GROUP_PTR_PROPERTIES;
    }

    isShowingEdgeTemplatePropertiesContext(): boolean {
        return (
            this.currentContext === EditorContextType.EDGE_TEMPLATE_PROPERTIES
        );
    }
}
