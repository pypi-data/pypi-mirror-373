// ============================================================================
// Editor Ui Mouse

import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { DispBase, DispBaseT, PointI } from "../canvas-shapes/DispBase";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import {
    CanvasInputDeltaI,
    CanvasInputPos,
    InputDelegateConstructorEditArgs,
    InputDelegateConstructorViewArgs,
} from "./PeekCanvasInputDelegateUtil.web";

export {
    CanvasInputDeltaI,
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
} from "./PeekCanvasInputDelegateUtil.web";

/*
 * This class manages the currently selected tool
 *
 */
export abstract class PeekCanvasInputDelegate {
    _CanvasInput = null;

    _lastMousePos: CanvasInputPos = new CanvasInputPos();

    /** The distance to move before its a drag * */
    readonly DRAG_START_THRESHOLD = 10;

    /** The time it takes to do a click, VS a click that moved slightly * */
    readonly DRAG_TIME_THRESHOLD = 200;

    protected constructor(
        protected viewArgs: InputDelegateConstructorViewArgs,
        protected editArgs: InputDelegateConstructorEditArgs,
        public NAME: EditorToolType,
    ) {}

    keyDown(event) {}

    keyPress(event) {}

    keyUp(event) {}

    mouseDown(event: MouseEvent, mouse: CanvasInputPos) {}

    // mouseSelectStart(event, mouse) {
    // };

    mouseMove(event: MouseEvent, mouse: CanvasInputPos) {}

    mouseUp(event: MouseEvent, mouse: CanvasInputPos) {}

    mouseDoubleClick(event: MouseEvent, mouse: CanvasInputPos) {}

    mouseWheel(event: MouseEvent, mouse: CanvasInputPos) {}

    touchStart(event: TouchEvent, mouse: CanvasInputPos) {}

    touchMove(event: TouchEvent, mouse: CanvasInputPos) {}

    touchEnd(event: TouchEvent, mouse: CanvasInputPos) {}

    shutdown() {}

    draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {}

    protected _hasPassedDragThreshold(m1: CanvasInputPos, m2: CanvasInputPos) {
        let distance =
            this.DRAG_START_THRESHOLD / this.viewArgs.config.viewPort.zoom;
        let d = false;
        // Time has passed
        d =
            d ||
            m2.time.getTime() - m1.time.getTime() > this.DRAG_TIME_THRESHOLD;
        // Mouse has moved
        d = d || Math.abs(m1.clientX - m2.clientX) > distance;
        d = d || Math.abs(m1.clientY - m2.clientY) > distance;

        return d;
    }

    /**
     * Set Last Mouse Pos
     *
     * Sets the last mouse pos depending on the snap
     *
     * @param the current mouse object
     * @return An object containing the delta
     */
    protected _setLastMousePos(
        inputPos: CanvasInputPos,
        snapping = true,
    ): CanvasInputDeltaI {
        let dx = inputPos.x - this._lastMousePos.x;
        let dy = inputPos.y - this._lastMousePos.y;
        let dClientX = inputPos.clientX - this._lastMousePos.clientX;
        let dClientY = inputPos.clientY - this._lastMousePos.clientY;

        if (snapping && this.viewArgs.config.editor.snapToGrid) {
            let snapSize = this.viewArgs.config.editor.snapSize;
            dx = dx - (dx % snapSize);
            dy = dy - (dy % snapSize);
            dClientX = dClientX - (dClientX % snapSize);
            dClientY = dClientY - (dClientY % snapSize);
        }

        this._lastMousePos.x += dx;
        this._lastMousePos.y += dy;
        this._lastMousePos.clientX += dClientX;
        this._lastMousePos.clientY += dClientY;

        return {
            dx: dx,
            dy: dy,
            dClientX: dClientX,
            dClientY: dClientY,
        };
    }

    protected _addBranchAnchor(x: number, y: number): void {
        if (this.editArgs.branchContext == null) return;

        let closestDisp = this.viewArgs.model.query.closestDispToPoint(
            x,
            y,
            (disp) => {
                let key = DispBase.key(disp);
                return key != null && key.length != 0;
            },
        );

        // TODO, See how close it is to other disps.
        if (closestDisp != null) {
            this.editArgs.branchContext.branchTuple.addAnchorDispKey(
                DispBase.key(closestDisp),
            );
        }
    }

    protected _checkNewShapeIsVisible(newShape: DispBaseT): void {
        if (DispBase.levelId(newShape) == null) {
            this.viewArgs.balloonMsgService.showError(
                "This shape was created with a null levelId," +
                    " Please set the default level in the diagram configuration.",
            );
            return;
        }

        if (DispBase.layerId(newShape) == null) {
            this.viewArgs.balloonMsgService.showError(
                "This shape was created with a null layerId," +
                    " Please set the default layer in the diagram configuration.",
            );
            return;
        }

        const level = DispBase.level(newShape);
        const layer = DispBase.layer(newShape);
        const zoom = this.viewArgs.config.viewPort.zoom;

        if (zoom < level.minZoom || level.maxZoom < zoom) {
            this.viewArgs.balloonMsgService.showError(
                "The shape just" +
                    " created has a level set that isn't currently visible." +
                    `${level.minZoom} to ${level.maxZoom} % zoom`,
            );
        }
    }
}
