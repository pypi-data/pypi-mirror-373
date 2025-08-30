import { CanvasInputPos } from "../canvas-input/PeekCanvasInputDelegateUtil.web";
import { EditPrimaryActionHandlerArgsI } from "./EditPrimaryActionHandlerArgsI";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";

export abstract class EditPrimaryActionHandlerDelegateABC {
    constructor(
        protected handlerArgs: EditPrimaryActionHandlerArgsI,
        protected canvasEditor: PeekCanvasEditor
    ) {
        //
    }

    abstract handlePrimaryAction(disp, position: CanvasInputPos): Promise<void>;
}
