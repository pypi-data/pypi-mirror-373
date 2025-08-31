import { takeUntil } from "rxjs/operators";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { PrivateDiagramPositionService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";
import {
    PrivateDiagramBranchContext,
    PrivateDiagramBranchService,
} from "@peek/peek_plugin_diagram/_private/branch";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { PeekCanvasInput } from "../canvas-input/PeekCanvasInput.web";
import { PeekCanvasInputEditSelectDelegate } from "../canvas-input/PeekCanvasInputEditSelectDelegate.web";
import { PeekCanvasInputSelectDelegate } from "../canvas-input/PeekCanvasInputSelectDelegate.web";
import { PeekCanvasModel } from "./PeekCanvasModel.web";
import { PeekCanvasConfig } from "./PeekCanvasConfig.web";
import { EditorToolType } from "./PeekCanvasEditorToolType.web";
import { DispLevel } from "@peek/peek_plugin_diagram/_private/lookups";
import { PeekCanvasEditorProps } from "./PeekCanvasEditorProps";
import { GridObservable } from "../cache/GridObservable.web";
import { EditPrimaryActionHandlerFactory } from "../edit-priamry-action-handlers/EditPrimaryActionHandlerFactory";

/**
 * Peek Canvas Editor
 *
 * This class is the central controller for Edit support.
 *
 */
export class PeekCanvasEditor {
    private _currentBranch: PrivateDiagramBranchContext | null = null;

    private readonly _props: PeekCanvasEditorProps;

    constructor(
        public balloonMsg: BalloonMsgService,
        public canvasInput: PeekCanvasInput,
        public canvasModel: PeekCanvasModel,
        private canvasConfig: PeekCanvasConfig,
        private gridObservable: GridObservable,
        public lookupService: PrivateDiagramLookupService,
        private positionService: PrivateDiagramPositionService,
        private branchService: PrivateDiagramBranchService,
        private lifecycleEventEmitter: NgLifeCycleEvents,
        private editPrimaryActionFactory: EditPrimaryActionHandlerFactory,
    ) {
        this.branchService
            .startEditingWithContextObservable()
            .pipe(takeUntil(lifecycleEventEmitter.onDestroyEvent))
            .subscribe((branchContext: PrivateDiagramBranchContext) => {
                this.gridObservable.resetAllDispComputedProperties();
                this._props.setCanvasData(this.modelSetId, this.coordSetId);

                if (this.branchContext) this.branchContext.close();

                this.branchContext = branchContext;

                this.branchContext.branchUpdatedObservable
                    .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
                    .subscribe((modelUpdateRequired: boolean) => {
                        if (modelUpdateRequired) {
                            this.canvasModel.recompileModel();
                            this.canvasModel.selection.clearSelection();
                            this.setEditorSelectTool();
                        }
                    });

                this.branchContext.open();

                const lastPos = branchContext.branchTuple.lastEditPosition;
                if (lastPos != null) {
                    this.positionService.position(
                        lastPos.coordSetKey,
                        lastPos.x,
                        lastPos.y,
                        lastPos.zoom,
                    );
                }

                this.setInputEditDelegate(PeekCanvasInputEditSelectDelegate);
                this.canvasModel.selection.clearSelection();
                this.canvasConfig.editor.active = true;
                this.canvasConfig.updateEditedBranch(
                    branchContext.branchTuple.key,
                );
                this.canvasConfig.setModelNeedsCompiling();
            });

        this.branchService
            .stopEditingObservable()
            .pipe(takeUntil(lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => {
                this.gridObservable.resetAllDispComputedProperties();
                if (this.branchContext) this.branchContext.close();

                this.branchContext = null;
                this.props.closeContext();
                this.canvasInput.setDelegate(PeekCanvasInputSelectDelegate);
                this.canvasConfig.editor.active = false;
                this.canvasModel.selection.clearSelection();
                this.canvasConfig.updateEditedBranch(null);
                this.canvasConfig.setModelNeedsCompiling();
            });

        this._props = new PeekCanvasEditorProps(this.lookupService);

        this.canvasModel.selection
            .selectionChangedObservable()
            .pipe(takeUntil(lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => {
                if (!this.canvasConfig.editor.active) return;
                this._props.setSelectedShapes(
                    this.canvasModel,
                    this._currentBranch.branchTuple,
                );
            });
    }

    // ---------------
    // Getters

    get modelSetId(): null | number {
        let cs = this.canvasConfig.controller.coordSet;
        return cs == null ? null : cs.modelSetId;
    }

    get coordSetId(): null | number {
        let cs = this.canvasConfig.controller.coordSet;
        return cs == null ? null : cs.id;
    }

    get props(): PeekCanvasEditorProps {
        return this._props;
    }

    // ---------------
    // Shape Props

    get branchContext(): PrivateDiagramBranchContext {
        return this._currentBranch;
    }

    // ---------------
    // Branch Context

    set branchContext(val: PrivateDiagramBranchContext | null) {
        this.canvasConfig.editor.activeBranchTuple = null;
        this._currentBranch = val;
        if (val != null) {
            this.canvasConfig.editor.activeBranchTuple = val.branchTuple;
            this.canvasConfig.setModelNeedsCompiling();
        }
    }

    dispPropsUpdated(touchUndo: boolean = true): void {
        this.canvasConfig.invalidate();

        if (this._currentBranch == null) return;

        this._currentBranch.branchTuple.touchUpdateDate(false);

        if (touchUndo) this._currentBranch.branchTuple.touchUndo();
    }

    // ---------------
    // Properties, used by UI mainly

    isEditing(): boolean {
        return this._currentBranch != null;
    }

    selectedTool(): EditorToolType {
        return this.canvasInput.selectedDelegateType();
    }

    isShapeSelected(): boolean {
        return true;
    }

    isLevelVisible(level: DispLevel): boolean {
        return level.isVisibleAtZoom(this.canvasConfig.viewPort.zoom);
    }

    setEditorSelectTool(): void {
        this.setInputEditDelegate(PeekCanvasInputEditSelectDelegate);
    }

    // ---------------
    // Methods called by toolbar

    closeEditor() {
        // TODO: Ask the user
        this.branchService.stopEditing();
    }

    save() {
        this._currentBranch.branchTuple.lastEditPosition = {
            x: this.canvasConfig.viewPort.pan.x,
            y: this.canvasConfig.viewPort.pan.y,
            zoom: this.canvasConfig.viewPort.zoom,
            coordSetKey: this.canvasConfig.coordSet.key,
        };

        this._currentBranch
            .save()
            .then(() => this.balloonMsg.showSuccess("Branch Save Successful"))
            .catch((e) =>
                this.balloonMsg.showError("Failed to save branch\n" + e),
            );
    }

    get canUndo(): boolean {
        return this._currentBranch?.branchTuple.canUndo;
    }

    doUndo(): void {
        this._currentBranch.branchTuple.doUndo(this.lookupService);
    }

    get canRedo(): boolean {
        return this._currentBranch?.branchTuple.canRedo;
    }

    doRedo(): void {
        this._currentBranch.branchTuple.doRedo(this.lookupService);
    }

    setInputEditDelegate(Delegate) {
        this.canvasInput.setDelegate(Delegate, {
            setEditorSelectTool: () => this.setEditorSelectTool(),
            doUndo: () => this.doUndo(),
            doRedo: () => this.doRedo(),
            branchContext: this.branchContext,
            editToolbarProps: this.props,
            lookupService: this.lookupService,
            editPrimaryActionFactory: this.editPrimaryActionFactory,
        });
    }

    invalidate(): void {
        this.canvasConfig.invalidate();
    }
}
