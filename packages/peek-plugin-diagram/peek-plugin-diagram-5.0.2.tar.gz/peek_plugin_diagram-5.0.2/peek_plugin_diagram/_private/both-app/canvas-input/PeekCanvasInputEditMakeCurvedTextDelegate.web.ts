import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { PeekCanvasInputEditMakeDispPolyDelegate } from "./PeekCanvasInputEditMakePolyDelegate.web";
import { InputDelegateConstructorViewArgs } from "./PeekCanvasInputDelegate.web";
import {
    CanvasInputPos,
    InputDelegateConstructorEditArgs,
} from "./PeekCanvasInputDelegateUtil.web";
import { DispCurvedText } from "../canvas-shapes/DispCurvedText";

export class PeekCanvasInputEditMakeCurvedTextDelegate extends PeekCanvasInputEditMakeDispPolyDelegate {
    static readonly TOOL_NAME = EditorToolType.EDIT_MAKE_CURVED_TEXT;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(
            viewArgs,
            editArgs,
            PeekCanvasInputEditMakeCurvedTextDelegate.TOOL_NAME,
        );

        this._reset();
    }

    protected override createDisp(inputPos: CanvasInputPos) {
        this.endCreateActionHandle = null;

        // Create the Disp - using DispCurvedText instead of DispPolyline
        this._creating = DispCurvedText.create(this.viewArgs.config.coordSet);

        // Add initial points
        DispCurvedText.addPoint(this._creating, {
            x: this._startMousePos.x,
            y: this._startMousePos.y,
        });
        this._setLastMousePos(this._startMousePos);

        // Add the second point for the path
        const geom = this._creating.g;
        geom.push(inputPos.x);
        geom.push(inputPos.y);

        // Link the Disp
        this.editArgs.lookupService._linkDispLookups(this._creating);

        // Add the shape to the branch
        this._creating =
            this.editArgs.branchContext.branchTuple.addOrUpdateDisp(
                this._creating,
                true,
            );

        this.viewArgs.model.recompileModel();
        this.viewArgs.model.selection.replaceSelection(this._creating);
        this._addBranchAnchor(inputPos.x, inputPos.y);
    }

    protected override _finaliseCreate() {
        this.endCreateActionHandle = null;

        if (this._creating == null) return;
        this._checkNewShapeIsVisible(this._creating);

        this._reset();

        this.editArgs.branchContext.branchTuple.touchUpdateDate(true);
        this.editArgs.branchContext.branchTuple.touchUndo();
        this.viewArgs.config.invalidate();
        this.editArgs.setEditorSelectTool();
    }
}
