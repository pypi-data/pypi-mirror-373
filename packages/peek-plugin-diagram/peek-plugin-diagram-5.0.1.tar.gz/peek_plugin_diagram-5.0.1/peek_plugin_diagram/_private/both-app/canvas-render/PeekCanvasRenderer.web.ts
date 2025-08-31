import { Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { PeekDispRenderFactory } from "./PeekDispRenderFactory.web";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PanI } from "../canvas/PeekInterfaces.web";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DrawModeE } from "./PeekDispRenderDelegateABC.web";
import { DispBase } from "../canvas-shapes/DispBase";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";

export class PeekCanvasPan implements PanI {
    x: number = 0.0;
    y: number = 0.0;
}

export interface RenderDrawArgs {
    ctx: any;
    zoom: number;
    pan: PeekCanvasPan;
    drawMode: DrawModeE;
}

/**
 * Editor Renderer This class is responsible for rendering the editor model
 */
export class PeekCanvasRenderer {
    drawEvent = new Subject<RenderDrawArgs>();
    private canvas: any = null;
    private isValid = false;
    private _zoom = 1.0;
    private _pan = new PeekCanvasPan();
    private lastZoomWhenShapesExisted: number = 1.0;

    constructor(
        private config: PeekCanvasConfig,
        private model: PeekCanvasModel,
        private dispDelegate: PeekDispRenderFactory,
        private lookupService: PrivateDiagramLookupService,
        private lifecycleEventEmitter: NgLifeCycleEvents,
    ) {}

    setCanvas(canvas) {
        this.canvas = canvas;
        this._init();
    }

    private invalidate() {
        this.isValid = false;
    }

    private _init() {
        // Start the draw timer.
        setInterval(() => this.draw(), this.config.renderer.drawInterval);

        // ------------------------------------------
        // Watch zoom

        this.config.viewPort.zoomChange
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe((newVal) => {
                if (newVal == this._zoom) return;
                this.zoom(newVal / this._zoom);
            });

        // ------------------------------------------
        // Apply pan

        this.config.viewPort.panChange
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => this.pan());

        // ------------------------------------------
        // Watch for canvas size changes

        this.config.canvas.windowChange
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => this.invalidate());

        // ------------------------------------------
        // Watch for invalidates

        this.config.renderer.invalidate
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => this.invalidate());
    }

    private currentViewArea() {
        let size = {
            w: this.canvas.clientWidth / this._zoom,
            h: this.canvas.clientHeight / this._zoom,
        };

        return new PeekCanvasBounds(
            this._pan.x - size.w / 2,
            this._pan.y - size.h / 2,
            size.w,
            size.h,
        );
    }

    private zoom(multiplier) {
        if (this._zoom * multiplier < this.config.viewPort.minZoom) {
            // MIN ZOOM
            multiplier = this.config.viewPort.minZoom / this._zoom;
        } else if (this._zoom * multiplier > this.config.viewPort.maxZoom) {
            // MAX ZOOM
            multiplier = this.config.viewPort.maxZoom / this._zoom;
        }

        this._zoom *= multiplier;
        this.config.viewPort.zoom = this._zoom;

        this.config.updateViewPortWindow(this.currentViewArea());

        this.invalidate();
    }

    private pan() {
        let pan = this.config.viewPort.pan;

        this._pan.x = pan.x;
        this._pan.y = pan.y;

        this.config.updateViewPortWindow(this.currentViewArea());

        this.invalidate();
    }

    // While draw is called as often as the INTERVAL variable demands,
    // It only ever does something if the canvas gets invalidated by our code
    private draw() {
        // if our state is invalid, redraw and validate!
        if (this.isValid) return;

        this.isValid = true;

        let ctx = this.canvas.getContext("2d");
        this.lookupService.updateCanvasPatterns(ctx);
        ctx.globalAlpha = 1.0;

        let disps = this.model.viewableDisps();
        let selectedDisps = this.model.selection.selectedDisps();

        let drawMode = this.config.editor.active
            ? DrawModeE.ForEdit
            : DrawModeE.ForView;

        // Clear canvas
        const w = this.canvas.width / this._zoom;
        const h = this.canvas.height / this._zoom;

        ctx.save();

        ctx.translate(this.canvas.width / 2.0, this.canvas.height / 2.0);
        ctx.scale(this._zoom, this._zoom);
        ctx.translate(-this._pan.x, -this._pan.y);

        ctx.fillStyle = this.config.renderer.backgroundColor;
        ctx.fillRect(this._pan.x - w, this._pan.y - h, w * 2, h * 2);

        // ** Add stuff you want drawn in the background all the time here **
        this._drawGrid(ctx);

        // draw all shapes, counting backwards for correct rendering
        // for (let i = dispObjs.length - 1; i != -1; i--) {

        let lastLayerId = null;

        // FIX: Fix for blank screens as the model set compiling
        // happens every 400ms and the rendering happens every 60ms
        // that's well over 340ms seconds of blank screen
        // If filtering out all visible disps would leave the diagram blank
        // then don't apply the filter.
        // This means that zooming though grid layers won't show blank canvases
        // but zooming within grid layers will still apply the decluttering.

        const willAnyShapesBeVisible =
            disps.filter((d) => DispBase.level(d).isVisibleAtZoom(this._zoom))
                .length !== 0;
        if (willAnyShapesBeVisible) {
            this.lastZoomWhenShapesExisted = this._zoom;
        }

        // draw all shapes, counting forwards for correct order or rendering
        for (let i = 0; i < disps.length; i++) {
            let disp = disps[i];

            // If the layer changes, apply the globalAlpha
            const layer = DispBase.layer(disp);
            if (layer.id !== lastLayerId) {
                lastLayerId = layer.id;
                ctx.globalAlpha = layer.opacity;
            }

            this.dispDelegate.draw(
                disp,
                ctx,
                this._zoom,
                this._pan,
                drawMode,
                this.lastZoomWhenShapesExisted,
            );
        }
        // Reset Global Alpha
        ctx.globalAlpha = 1.0;

        // draw selection
        // right now this is just a stroke along the edge of the selected Shape
        for (let i = 0; i < selectedDisps.length; i++) {
            let dispObj = selectedDisps[i];
            this.dispDelegate.drawSelected(
                dispObj,
                ctx,
                this._zoom,
                this._pan,
                drawMode,
            );
        }

        if (selectedDisps.length == 1 && drawMode == DrawModeE.ForEdit) {
            this.dispDelegate.drawEditHandles(
                selectedDisps[0],
                ctx,
                this._zoom,
                this._pan,
            );
        }

        // ** Add stuff you want drawn on top all the time here **
        // Tell the canvas mouse handler to draw what ever its got going on.
        this.drawEvent.next({
            ctx,
            zoom: this._zoom,
            pan: this._pan,
            drawMode,
        });

        // Finally render anything with the overrides
        for (const override of this.model.overrides) {
            override.draw(ctx, this._zoom);
        }

        ctx.restore();
    }

    /**
     * Draw Selection Box Draws a selection box on the canvas
     */
    private _drawGrid(ctx) {
        // Avoid Typescript complaining about parseInt
        function trunc(num: any): number {
            return parseInt(num);
        }

        if (!this.config.renderer.grid.show) return;

        let area = this.config.viewPort.window;
        let zoom = this.config.viewPort.zoom;

        let unscale = 1.0 / zoom;

        let gridSize = this.config.controller.coordSet.gridSizeForZoom(zoom);

        let minX = area.x;
        let minY = area.y;
        let maxX = area.x + area.w;
        let maxY = area.y + area.h;

        // Round the X min/max
        let minGridX = trunc(minX / gridSize.xGrid);
        let maxGridX = trunc(maxX / gridSize.xGrid) + 1;

        // Round the Y min/max
        let minGridY = trunc(minY / gridSize.yGrid);
        let maxGridY = trunc(maxY / gridSize.yGrid) + 1;

        ctx.lineWidth = this.config.renderer.grid.lineWidth / this._zoom;
        ctx.strokeStyle = this.config.renderer.grid.color;

        ctx.fillStyle = this.config.renderer.grid.color;
        ctx.textAlign = "start";
        ctx.textBaseline = "top";
        ctx.font = this.config.renderer.grid.font;

        // Draw the vertical lines
        for (let x = minGridX; x < maxGridX; x++) {
            ctx.beginPath();
            ctx.moveTo(x * gridSize.xGrid, minY);
            ctx.lineTo(x * gridSize.xGrid, maxY);
            ctx.stroke();
        }

        // Draw the horizontal lines
        for (let y = minGridY; y < maxGridY; y++) {
            ctx.beginPath();
            ctx.moveTo(minX, y * gridSize.yGrid);
            ctx.lineTo(maxX, y * gridSize.yGrid);
            ctx.stroke();
        }

        // Draw the vertical lines
        for (let x = minGridX; x < maxGridX; x++) {
            for (let y = minGridY; y < maxGridY; y++) {
                let text = x.toString() + "x" + y.toString();

                // draw fixed size font
                ctx.save();
                ctx.translate(x * gridSize.xGrid + 15, y * gridSize.yGrid + 15);
                ctx.scale(unscale, unscale);
                ctx.fillText(text, 0, 0);
                ctx.restore();
            }
        }
    }

    /**
     * Return the size of the canvas
     */
    private canvasInnerBounds() {
        let c = this.canvas;
        return new PeekCanvasBounds(0, 0, c.width, c.height);
    }
}
