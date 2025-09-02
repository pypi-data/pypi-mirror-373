import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import {
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
    PeekCanvasInputDelegate,
} from "./PeekCanvasInputDelegate.web";
import { DispGroupPointer } from "../canvas-shapes/DispGroupPointer";
import { PointI } from "../canvas-shapes/DispBase";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputMakeDispGroupPtrVertexDelegate extends PeekCanvasInputDelegate {
    static readonly TOOL_NAME = EditorToolType.EDIT_MAKE_DISP_GROUP_PTR_VERTEX;

    // Used to detect dragging and its the mouse position we use
    private _startMousePos: CanvasInputPos | null = null;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(
            viewArgs,
            editArgs,
            PeekCanvasInputMakeDispGroupPtrVertexDelegate.TOOL_NAME,
        );

        this._reset();
    }

    _reset() {
        // See mousedown and mousemove events for explanation
        this._startMousePos = null;
        this._lastMousePos = null;
    }

    // ============================================================================
    // Editor Ui Mouse

    // ---------------
    // Map mouse events
    override mouseDown(event: MouseEvent, inputPos: CanvasInputPos) {
        this.inputStart(inputPos);
    }

    override mouseMove(event: MouseEvent, inputPos: CanvasInputPos) {
        this.inputMove(inputPos);
    }

    override mouseUp(event: MouseEvent, inputPos: CanvasInputPos) {
        this.inputEnd(inputPos);
    }

    // ---------------
    // Map touch events
    override touchStart(event: TouchEvent, inputPos: CanvasInputPos) {
        this.inputStart(inputPos);
    }

    override touchMove(event: TouchEvent, inputPos: CanvasInputPos) {
        this.inputMove(inputPos);
    }

    override touchEnd(event: TouchEvent, inputPos: CanvasInputPos) {
        this.inputEnd(inputPos);
    }

    // ---------------
    // Misc delegate methods
    delegateWillBeTornDown() {
        this._finaliseCreate();
    }

    override draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {}

    // ---------------
    // Start logic

    _finaliseCreate() {
        this.editArgs.editToolbarProps.showGroupPtrProperties();
        // No check for a group pointer as it doesn't have one shape
        // this._checkNewShapeIsVisible(this._creating);
        this._reset();
        this.viewArgs.config.invalidate();
    }

    private inputStart(inputPos: CanvasInputPos) {
        this._finaliseCreate();
        this._startMousePos = inputPos;
    }

    private inputMove(inputPos: CanvasInputPos) {}

    private inputEnd(inputPos: CanvasInputPos) {
        if (this._hasPassedDragThreshold(this._startMousePos, inputPos)) {
            this._reset();
            return;
        }

        this.createDisp(inputPos.x, inputPos.y);
    }

    private createDisp(x: number, y: number) {
        // Create the Disp
        let created = DispGroupPointer.create(this.viewArgs.config.coordSet);
        DispGroupPointer.setCenterPoint(created, x, y);

        this.editArgs.lookupService._linkDispLookups(created);

        // Add the shape to the branch
        created = this.editArgs.branchContext.branchTuple.addOrUpdateDisp(
            created,
            true,
        );
        this.editArgs.branchContext.branchTuple.touchUndo();

        this.viewArgs.model.recompileModel();
        this.viewArgs.model.selection.replaceSelection(<any>created);

        this._addBranchAnchor(x, y);
        this.editArgs.setEditorSelectTool();
    }
}
