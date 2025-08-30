import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { PeekCanvasInputEditMakeDispPolyDelegate } from "./PeekCanvasInputEditMakePolyDelegate.web";
import { InputDelegateConstructorViewArgs } from "./PeekCanvasInputDelegate.web";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputEditMakeDispPolylinDelegate extends PeekCanvasInputEditMakeDispPolyDelegate {
    static readonly TOOL_NAME = EditorToolType.EDIT_MAKE_POLYLINE;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(
            viewArgs,
            editArgs,
            PeekCanvasInputEditMakeDispPolylinDelegate.TOOL_NAME,
        );

        this._reset();
    }
}
