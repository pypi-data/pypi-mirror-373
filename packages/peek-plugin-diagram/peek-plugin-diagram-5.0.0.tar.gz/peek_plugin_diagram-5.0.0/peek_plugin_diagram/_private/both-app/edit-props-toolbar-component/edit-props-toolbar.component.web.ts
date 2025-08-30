import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { EditorContextType } from "../canvas/PeekCanvasEditorProps";

@Component({
    selector: "pl-diagram-edit-props-toolbar",
    templateUrl: "edit-props-toolbar.component.web.html",
    styleUrls: ["edit-props-toolbar.component.web.scss"],
})
export class EditPropsToolbarComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;

    currentContext: EditorContextType = EditorContextType.NONE;

    constructor() {
        super();
    }

    override ngOnInit() {
        this.canvasEditor.props.contextPanelObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((val: EditorContextType) => {
                this.currentContext = val;
            });
    }

    isToolbarShown(): boolean {
        return this.canvasEditor.isEditing();
    }

    // Branch Properties
    showBranchProperties(): void {
        this.canvasEditor.props.showBranchProperties();
    }

    isBranchPropertiesActive(): boolean {
        return this.currentContext == EditorContextType.BRANCH_PROPERTIES;
    }

    // Shape Properties
    showShapeProperties(): void {
        this.canvasEditor.props.showShapeProperties();
    }

    isShapePropertiesActive(): boolean {
        return this.currentContext == EditorContextType.SHAPE_PROPERTIES;
    }

    isShapePropertiesShown(): boolean {
        return this.canvasEditor.props.shapePanelContext != null;
    }

    // GroupPtr Properties
    showGroupPtrProperties(): void {
        this.canvasEditor.props.showGroupPtrProperties();
    }

    isGroupPtrPropertiesActive(): boolean {
        return this.currentContext == EditorContextType.GROUP_PTR_PROPERTIES;
    }

    isGroupPtrPropertiesShown(): boolean {
        return this.canvasEditor.props.groupPtrPanelContext != null;
    }

    // EdgeTemplate Properties
    showEdgeTemplateProperties(): void {
        this.canvasEditor.props.showEdgeTemplateProperties();
    }

    isEdgeTemplatePropertiesActive(): boolean {
        return (
            this.currentContext == EditorContextType.EDGE_TEMPLATE_PROPERTIES
        );
    }

    isEdgeTemplatePropertiesShown(): boolean {
        return this.canvasEditor.props.edgeTemplatePanelContext != null;
    }

    // LiveDB Properties
    showLiveDbProperties(): void {
        this.canvasEditor.props.showLiveDbProperties();
    }

    isLiveDbPropertiesActive(): boolean {
        return false;
    }

    isLiveDbPropertiesShown(): boolean {
        return false; //this.canvasEditor.isShapeSelected();
    }
}
