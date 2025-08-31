import {
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
    PeekCanvasInputDelegate,
} from "./PeekCanvasInputDelegate.web";
import { DispText } from "../canvas-shapes/DispText";
import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import { PointI } from "../canvas-shapes/DispBase";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputEditMakeTextDelegate extends PeekCanvasInputDelegate {
    static readonly TOOL_NAME = EditorToolType.EDIT_MAKE_TEXT;

    // Stores the text disp being created
    private _creating = null;

    // Used to detect dragging and its the mouse position we use
    private _startMousePos: CanvasInputPos | null = null;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(
            viewArgs,
            editArgs,
            PeekCanvasInputEditMakeTextDelegate.TOOL_NAME,
        );

        this.viewArgs.model.selection.clearSelection();
        this._reset();
    }

    _reset() {
        this._creating = null;
        this._startMousePos = null;

        // See mousedown and mousemove events for explanation
        this._startMousePos = null;
        this._lastMousePos = new CanvasInputPos();
    }

    // ============================================================================
    // Editor Ui Mouse

    override keyPress(event) {
        if (!this._creating) return;

        let enteredText = DispText.text(this._creating);

        if (event.keyCode == 8) {
            // Backspace
            if (enteredText && enteredText.length)
                enteredText = enteredText.substr(0, enteredText.length - 1);
            else enteredText = "";
            this._creating.setText(enteredText);
            this.viewArgs.config.invalidate();
            return;
        }

        if (event.keyCode == 13) {
            // Enter
            this._finaliseCreate();
        }

        let inp = String.fromCharCode(event.keyCode);
        if (/[a-zA-Z0-9-_ .,`"'|~!@#$%^&*()-=+{}\[\]\\:;<>\/?]/.test(inp)) {
            enteredText = (enteredText || "") + inp;
            this._creating.setText(enteredText);
            this.viewArgs.config.invalidate();
            return;
        }
    }

    override keyUp(event) {
        if (!this._creating) return;

        if (
            event.keyCode == 46 || // delete
            event.keyCode == 27
        ) {
            // escape
            this._reset();
            return;
        }
    }

    override mouseDown(event, mouse) {
        this._startMousePos = mouse;
    }

    override mouseUp(event, mouse: CanvasInputPos) {
        if (this._hasPassedDragThreshold(this._startMousePos, mouse)) {
            this._reset();
            return;
        }

        this.createDisp(mouse.x, mouse.y);
        // Show the edit text box
        this.editArgs.editPrimaryActionFactory.handlePrimaryAction(
            this._creating,
            mouse,
        );
        this._finaliseCreate();
    }

    override touchStart(event: TouchEvent, mouse: CanvasInputPos) {
        this.mouseDown(event, mouse);
    }

    override touchEnd(event: TouchEvent, mouse: CanvasInputPos) {
        this.mouseUp(event, mouse);
    }

    delegateWillBeTornDown() {
        this._finaliseCreate();
    }

    override draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {}

    _finaliseCreate() {
        if (this._creating == null) return;
        this._checkNewShapeIsVisible(this._creating);
        this._reset();
        this.viewArgs.config.invalidate();
    }

    private createDisp(x: number, y: number) {
        // Create the Disp
        this._creating = DispText.create(this.viewArgs.config.coordSet);
        DispText.setCenterPoint(this._creating, x, y);
        this.editArgs.lookupService._linkDispLookups(this._creating);

        // Add the shape to the branch
        this._creating =
            this.editArgs.branchContext.branchTuple.addOrUpdateDisp(
                this._creating,
                true,
            );
        this.editArgs.branchContext.branchTuple.touchUndo();

        this.viewArgs.model.recompileModel();

        this._addBranchAnchor(x, y);
        this.editArgs.setEditorSelectTool();

        this.viewArgs.model.selection.replaceSelection(this._creating);
        this.editArgs.editToolbarProps.showShapeProperties();
    }
}
