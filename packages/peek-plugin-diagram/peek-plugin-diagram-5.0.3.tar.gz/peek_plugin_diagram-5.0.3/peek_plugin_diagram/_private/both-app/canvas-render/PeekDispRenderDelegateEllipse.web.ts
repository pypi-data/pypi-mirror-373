import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import {
    DrawModeE,
    PeekDispRenderDelegateABC,
} from "./PeekDispRenderDelegateABC.web";
import { DispEllipse, DispEllipseT } from "../canvas-shapes/DispEllipse";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DispBaseT, PointI } from "../canvas-shapes/DispBase";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";

export class PeekDispRenderDelegateEllipse extends PeekDispRenderDelegateABC {
    constructor(config: PeekCanvasConfig, model: PeekCanvasModel) {
        super(config, model);
    }

    updateBounds(disp: DispBaseT): void {
        let ellipse = <DispEllipseT>disp;

        let centerX = DispEllipse.centerPointX(ellipse);
        let centerY = DispEllipse.centerPointY(ellipse);
        let xRadius = DispEllipse.xRadius(ellipse);
        let yRadius = DispEllipse.yRadius(ellipse);

        //self._bounds.x = self.left;
        //self._bounds.y = self.top;
        //self._bounds.w = self.width;
        //self._bounds.h = self.height;
        disp.bounds = new PeekCanvasBounds(
            centerX - xRadius,
            centerY - yRadius,
            2 * xRadius,
            2 * yRadius,
        );
    }

    draw(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        const lineStyle = DispEllipse.lineStyle(disp);

        // Null colors are also not drawn
        const fillColor = DispEllipse.fillColor(disp)?.getColor(
            this.config.isLightMode
        );

        // Null colors are also not drawn
        const fillColorPattern = DispEllipse.fillColor(disp)?.getFillPattern(
            this.config.isLightMode
        );
        const lineColor = lineStyle
            ? DispEllipse.lineColor(disp)?.getColor(this.config.isLightMode)
            : null;

        let xRadius = DispEllipse.xRadius(disp);
        let yRadius = DispEllipse.yRadius(disp);
        let rotationRadian = (DispEllipse.rotation(disp) / 180.0) * Math.PI;
        let startAngle = DispEllipse.startAngle(disp);
        let endAngle = DispEllipse.endAngle(disp);
        let lineWidth = DispEllipse.lineWidth(disp);

        let yScale = yRadius / xRadius;

        // save state
        ctx.save();
        ctx.translate(
            DispEllipse.centerPointX(disp),
            DispEllipse.centerPointY(disp),
        );
        ctx.scale(1, yScale);
        ctx.rotate(rotationRadian);

        let startRadian = (startAngle / 180.0) * Math.PI;
        let endRadian = (endAngle / 180.0) * Math.PI;

        ctx.beginPath();
        ctx.arc(0, 0, xRadius, startRadian, endRadian, true);
        //ctx.closePath();

        if (fillColor || fillColorPattern) {
            ctx.lineTo(0, 0); // Make it fill to the center, not just the ends of the arc
            if (fillColor) {
                ctx.fillStyle = fillColor;
                ctx.fill();
            }
            if (fillColorPattern) {
                ctx.fillStyle = fillColorPattern;
                ctx.fill();
            }
        }

        if (lineColor) {
            ctx.strokeStyle = lineColor;
            ctx.lineWidth = lineStyle.scalable ? lineWidth : lineWidth / zoom;
            ctx.stroke();
        }

        // restore to original state
        ctx.restore();
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

    drawEditHandles(disp, ctx, zoom: number, pan: PointI) {}
}
