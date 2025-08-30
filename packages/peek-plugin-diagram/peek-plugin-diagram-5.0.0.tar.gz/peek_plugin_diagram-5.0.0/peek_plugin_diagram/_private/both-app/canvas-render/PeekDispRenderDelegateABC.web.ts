import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DispBaseT, DispHandleI, PointI } from "../canvas-shapes/DispBase";
import { DispFactory } from "../canvas-shapes/DispFactory";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { DrawModeE } from "./PeekDispRenderDrawModeE.web";

export { DrawModeE } from "./PeekDispRenderDrawModeE.web";

export abstract class PeekDispRenderDelegateABC {
    protected constructor(
        protected config: PeekCanvasConfig,
        protected model: PeekCanvasModel,
    ) {}

    abstract updateBounds(disp: DispBaseT, zoom: number): void;

    abstract draw(disp, ctx, zoom: number, pan: PointI, drawMode: DrawModeE);

    abstract drawSelected(
        disp,
        ctx,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE,
    );

    abstract drawEditHandles(disp, ctx, zoom: number, pan: PointI);

    handles(disp: DispBaseT, zoom: number): DispHandleI[] {
        const margin = this.config.editor.resizeHandleMargin;
        const width = this.config.editor.resizeHandleWidth / zoom;

        const handles: DispHandleI[] = DispFactory.wrapper(disp).handlePoints(
            disp,
            margin,
        );

        const halfWidth = width / 2.0;

        return handles.map((handle: DispHandleI, index: number) => {
            handle.box = new PeekCanvasBounds(
                handle.center.x - halfWidth,
                handle.center.y - halfWidth,
                width,
                width,
            );
            handle.handleIndex = index;

            return handle;
        });
    }
}
