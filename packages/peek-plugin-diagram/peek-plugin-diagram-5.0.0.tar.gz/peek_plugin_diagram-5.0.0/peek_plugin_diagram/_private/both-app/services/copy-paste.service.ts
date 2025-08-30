import { Injectable } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { DispBase, DispBaseT } from "../canvas-shapes/DispBase";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { DispGroupPointer } from "../canvas-shapes/DispGroupPointer";

interface CopiedDispI {
    disp: DispBaseT;
    childShapes?: DispBaseT[] | null;
}

/** Copy Paste Service
 *
 * This class is responsible providing copy and paste support
 *
 */
@Injectable()
export class CopyPasteService extends NgLifeCycleEvents {
    private clipboard: CopiedDispI[] = [];
    private clipboardBounds: PeekCanvasBounds | null = null;
    private model: PeekCanvasModel;
    private config: PeekCanvasConfig;
    private editor: PeekCanvasEditor;

    constructor() {
        super();
    }

    setModel(model: PeekCanvasModel): void {
        this.model = model;
    }

    setConfig(config: PeekCanvasConfig): void {
        this.config = config;
    }

    setEditor(editor: PeekCanvasEditor): void {
        this.editor = editor;
    }

    get canCopy(): boolean {
        return this.model?.selection?.hasSelection;
    }

    doCopy() {
        if (!this.canCopy) return;

        this.clipboardBounds = null;
        this.clipboard = [];
        for (const shape of this.model.selection.selectedDisps()) {
            if (this.clipboardBounds == null) {
                this.clipboardBounds = new PeekCanvasBounds(shape.bounds);
            } else {
                this.clipboardBounds.increaseFromBounds(shape.bounds);
            }

            const clonedShape: CopiedDispI = {
                disp: DispBase.cloneDisp(shape, { resetUniques: true }),
            };

            // Clone any child shapes
            if (DispGroupPointer.disps(shape) != null) {
                clonedShape.childShapes = [];
                for (const childDisp of DispGroupPointer.disps(shape)) {
                    clonedShape.childShapes.push(
                        DispBase.cloneDisp(childDisp, { resetUniques: true }),
                    );
                }
            }

            this.clipboard.push(clonedShape);
        }
    }

    get canPaste(): boolean {
        return this.clipboard.length !== 0;
    }

    doPaste() {
        if (!this.canPaste) return;

        const mouse = {
            x: this.config.mouse.currentViewPortPosition.x,
            y: this.config.mouse.currentViewPortPosition.y,
        };

        const oldCenter = this.clipboardBounds.center();
        const delta = {
            x: mouse.x - oldCenter.x,
            y: mouse.y - oldCenter.y,
        };

        const branchTuple = this.editor?.branchContext?.branchTuple;

        const shapesToAdd = [];
        for (const shape of this.clipboard) {
            // Clone the single shape
            let clone = DispBase.cloneDisp(shape.disp);
            DispBase.deltaMove(clone, delta.x, delta.y);

            // If it has no children, add it to the array and continue
            if (shape.childShapes == null) {
                shapesToAdd.push(clone);
                continue;
            }

            // We need an ID for the child shapes, so we need to add the parent
            // shape.
            clone = branchTuple.addOrUpdateDisp(clone, true);
            for (const childShape of shape.childShapes) {
                const childClone = DispBase.cloneDisp(childShape);
                DispBase.deltaMove(childClone, delta.x, delta.y);
                DispBase.setGroupId(childClone, DispBase.id(clone));
                shapesToAdd.push(childClone);
            }
        }

        branchTuple.addOrUpdateDisps(shapesToAdd);
        branchTuple.touchUndo();
    }
}
