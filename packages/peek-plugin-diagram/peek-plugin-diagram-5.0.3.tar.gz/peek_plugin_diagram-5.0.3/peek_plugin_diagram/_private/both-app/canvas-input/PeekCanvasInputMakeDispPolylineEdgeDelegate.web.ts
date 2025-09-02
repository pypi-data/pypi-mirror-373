import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import {
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
} from "./PeekCanvasInputDelegate.web";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";
import { DispPolyline, DispPolylineT } from "../canvas-shapes/DispPolyline";
import { PeekCanvasInputEditMakeDispPolyDelegate } from "./PeekCanvasInputEditMakePolyDelegate.web";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputMakeDispPolylineEdgeDelegate extends PeekCanvasInputEditMakeDispPolyDelegate {
    static readonly TOOL_NAME = EditorToolType.EDIT_MAKE_DISP_POLYLINE_EDGE;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(
            viewArgs,
            editArgs,
            PeekCanvasInputMakeDispPolylineEdgeDelegate.TOOL_NAME,
        );

        this._reset();
    }

    protected override createDisp(inputPos: CanvasInputPos) {
        super.createDisp(inputPos);

        const coordSet = <ModelCoordSet>this.viewArgs.config.coordSet;
        const disp = <DispPolylineT>this._creating;
        DispPolyline.setTargetEdgeTemplateName(
            disp,
            coordSet.editDefaultEdgeCoordSetId,
            coordSet.editDefaultEdgeGroupName,
        );
    }
}
