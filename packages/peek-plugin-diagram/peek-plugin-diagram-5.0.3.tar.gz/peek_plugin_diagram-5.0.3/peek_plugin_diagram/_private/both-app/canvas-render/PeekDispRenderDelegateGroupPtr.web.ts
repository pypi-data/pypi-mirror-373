import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DrawModeE,
    PeekDispRenderDelegateABC,
} from "./PeekDispRenderDelegateABC.web";
import { DispBaseT, DispHandleTypeE, PointI } from "../canvas-shapes/DispBase";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import {
    DispGroupPointer,
    DispGroupPointerT,
} from "../canvas-shapes/DispGroupPointer";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";

export class PeekDispRenderDelegateGroupPtr extends PeekDispRenderDelegateABC {
    constructor(config: PeekCanvasConfig, model: PeekCanvasModel) {
        super(config, model);
    }

    updateBounds(disp: DispBaseT): void {
        disp.bounds = PeekCanvasBounds.fromGeom(DispGroupPointer.geom(disp));
    }

    draw(disp: DispBaseT, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        const dispGroup = <DispGroupPointerT>disp;
        if (DispGroupPointer.targetGroupName(dispGroup) != null) return;

        this.drawNoTarget(dispGroup, ctx, zoom, pan, drawMode);
    }

    drawSelected(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        let bounds = disp.bounds;
        if (bounds == null) return;

        // DRAW THE SELECTED BOX
        let selectionConfig =
            this.config.getSelectionDrawDetailsForDrawMode(drawMode);

        // Move the selection line a bit away from the object
        let offset = (selectionConfig.width + selectionConfig.lineGap) / zoom;

        let twiceOffset = 2 * offset;
        let x = bounds.x - offset;
        let y = bounds.y - offset;
        let w = bounds.w + twiceOffset;
        let h = bounds.h + twiceOffset;

        ctx.dashedRect(x, y, w, h, selectionConfig.dashLen / zoom);
        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();
    }

    drawEditHandles(disp, ctx, zoom: number, pan: PointI) {
        // DRAW THE EDIT HANDLES
        ctx.fillStyle = this.config.editor.selectionHighlightColor;
        const handles = this.handles(disp, zoom);

        for (const handle of handles) {
            const b = handle.box;
            ctx.beginPath();
            switch (handle.handleType) {
                case DispHandleTypeE.freeRotate:
                    ctx.arc(
                        b.x + b.w / 2,
                        b.y + b.h / 2,
                        b.h / 2,
                        0,
                        2 * Math.PI,
                    );
                    break;
                case DispHandleTypeE.snapRotate:
                    ctx.rect(b.x, b.y, b.w, b.h);
                    break;
                default:
                    // pass
                    break;
            }
            ctx.fill();
        }
    }

    /** Draw No Target
     *
     * If the DispGroup is unset and invisible, then we need to draw something to
     * show that it's there.
     *
     * @param dispGroup
     * @param ctx
     * @param zoom
     * @param pan
     * @param drawMode
     */
    private drawNoTarget(
        dispGroup: DispGroupPointerT,
        ctx,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE,
    ) {
        if (drawMode != DrawModeE.ForEdit) return;

        const box = PeekCanvasBounds.fromGeom(DispGroupPointer.geom(dispGroup));
        const selectionConfig = this.config.renderer.editSelection;

        // We'll use the margin from the selected config if there is just one point.
        if (box.w == 0) {
            let offset =
                (selectionConfig.width + selectionConfig.lineGap) / zoom;
            box.x -= offset;
            box.y -= offset;
            box.w = 2 * offset;
            box.h = 2 * offset;
        }

        const rotation = DispGroupPointer.rotation(dispGroup);
        const center = box.center();

        ctx.save();
        if (rotation != 0) {
            ctx.translate(center.x, center.y);
            ctx.rotate((rotation * Math.PI) / 180);
            ctx.translate(-center.x, -center.y);
        }

        ctx.beginPath();
        // Top left to Bottom right
        ctx.moveTo(box.x, box.y);
        ctx.lineTo(box.x + box.w, box.y + box.h);

        // Bottom left to top right
        ctx.moveTo(box.x, box.y + box.h);
        ctx.lineTo(box.x + box.w, box.y);

        ctx.strokeStyle = selectionConfig.color;
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();

        // Show an indication of rotation
        ctx.beginPath();
        // Top left to Bottom right
        ctx.moveTo(box.x, box.y);
        ctx.lineTo(box.x + box.w / 2, box.y + box.h / 2);

        ctx.strokeStyle = "red";
        ctx.lineWidth = selectionConfig.width / zoom;
        ctx.stroke();

        ctx.restore();
    }
}
