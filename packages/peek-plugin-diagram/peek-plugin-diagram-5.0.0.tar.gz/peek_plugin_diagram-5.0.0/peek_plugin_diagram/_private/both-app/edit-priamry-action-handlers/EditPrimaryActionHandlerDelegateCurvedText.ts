import { EditPrimaryActionHandlerDelegateABC } from "./EditPrimaryActionHandlerDelegateABC";
import { CanvasInputPos } from "../canvas-input/PeekCanvasInputDelegateUtil.web";

export class EditPrimaryActionDelegateHandlerCurvedText extends EditPrimaryActionHandlerDelegateABC {
    handlePrimaryAction(disp, position: CanvasInputPos): Promise<void> {
        return new Promise<void>((resolve) => {
            this.handlerArgs.textActionComponent.open(
                disp,
                {
                    x: position.mouseX,
                    y: position.mouseY,
                },
                () => {
                    this.canvasEditor.dispPropsUpdated();
                    resolve();
                },
                () => {
                    this.canvasEditor.invalidate();
                },
            );
        });
    }
}
