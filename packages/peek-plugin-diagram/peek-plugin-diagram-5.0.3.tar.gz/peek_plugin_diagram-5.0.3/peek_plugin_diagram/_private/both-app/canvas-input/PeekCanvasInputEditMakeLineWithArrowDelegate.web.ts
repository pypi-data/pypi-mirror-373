import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { PeekCanvasInputEditMakeDispPolyDelegate } from "./PeekCanvasInputEditMakePolyDelegate.web";
import { InputDelegateConstructorViewArgs } from "./PeekCanvasInputDelegate.web";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputEditMakeLineWithArrowDelegate extends PeekCanvasInputEditMakeDispPolyDelegate {
    static readonly TOOL_NAME = EditorToolType.EDIT_MAKE_LINE_WITH_ARROW;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(
            viewArgs,
            editArgs,
            PeekCanvasInputEditMakeLineWithArrowDelegate.TOOL_NAME,
        );

        this._reset();
    }
}
