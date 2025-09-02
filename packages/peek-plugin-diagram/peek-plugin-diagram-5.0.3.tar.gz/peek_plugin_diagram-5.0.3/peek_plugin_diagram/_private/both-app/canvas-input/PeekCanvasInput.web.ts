import { takeUntil } from "rxjs/operators";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { PeekDispRenderFactory } from "../canvas-render/PeekDispRenderFactory.web";
import { PeekCanvasInputDelegate } from "./PeekCanvasInputDelegate.web";
import {
    CanvasInputPos,
    disableContextMenu,
    InputDelegateConstructorEditArgs,
    InputDelegateConstructorViewArgs,
} from "./PeekCanvasInputDelegateUtil.web";
import { PeekCanvasInputSelectDelegate } from "./PeekCanvasInputSelectDelegate.web";
import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { PointI } from "../canvas-shapes/DispBase";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import { PeekCanvasActioner } from "../canvas/PeekCanvasActioner";
import { CopyPasteService } from "../services/copy-paste.service";
import { ContextMenuService } from "../services/context-menu.service";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { PrivateDiagramPositionService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";

/** Peek Canvas Input
 *
 * This class manages the user input of the canvas
 *
 */
export class PeekCanvasInput {
    private _delegate: PeekCanvasInputDelegate = null;

    private canvas: HTMLCanvasElement | null = null;

    // These offsets are calculated on the size and position of the canvas in the HTML
    // page. When added to the mouse event coordinates, they convert the mouse event
    // coordinates to be relative to the center of the canvas.
    private mouseOffsetX: number = 0;
    private mouseOffsetY: number = 0;

    constructor(
        private config: PeekCanvasConfig,
        private model: PeekCanvasModel,
        private renderFactory: PeekDispRenderFactory,
        private lifecycleEventEmitter,
        private objectPopupService,
        private copyPasteService: CopyPasteService,
        private contextMenuService: ContextMenuService,
        private actioner: PeekCanvasActioner,
        private balloonMsgService: BalloonMsgService,
        private positionService: PrivateDiagramPositionService,
    ) {
        this.delegateFinished();
    }

    setDelegate(
        Delegate,
        editArgs: InputDelegateConstructorEditArgs | null = null,
    ) {
        if (this._delegate) this._delegate.shutdown();

        const viewDelegateArgs: InputDelegateConstructorViewArgs = {
            input: this,
            config: this.config,
            model: this.model,
            renderFactory: this.renderFactory,
            objectPopupService: this.objectPopupService,
            copyPasteService: this.copyPasteService,
            contextMenuService: this.contextMenuService,
            actioner: this.actioner,
            balloonMsgService: this.balloonMsgService,
            positionService: this.positionService,
        };

        this._delegate = new Delegate(viewDelegateArgs, editArgs);

        this.config.mouse.currentDelegateName = Delegate.TOOL_NAME;
    }

    delegateFinished() {
        this.setDelegate(PeekCanvasInputSelectDelegate);
    }

    selectedDelegateType(): EditorToolType {
        return this.config.mouse.currentDelegateName;
    }

    selectedDelegate(): PeekCanvasInputDelegate {
        return this._delegate;
    }

    // Creates an object with x and y defined, set to the mouse position relative to
    // the state's canvas
    // If you want to be super-correct this can be tricky, we have to worry about
    // padding and borders
    _getMouse(e): CanvasInputPos {
        let pageX = e.pageX;
        let pageY = e.pageY;

        if (pageX == null) {
            if (e.changedTouches != null && e.changedTouches.length >= 0) {
                let touch = e.changedTouches[0];
                pageX = touch.pageX;
                pageY = touch.pageY;
            } else {
                console.log("ERROR: Failed to determine pan coordinates");
            }
        }

        let mx = pageX - this.mouseOffsetX;
        let my = pageY - this.mouseOffsetY;

        let clientX = mx;
        let clientY = my;

        // Apply canvas scale and pan
        let zoom = this.config.viewPort.zoom;
        let pan = this.config.viewPort.pan;
        mx = mx / zoom + pan.x;
        my = my / zoom + pan.y;

        if (isNaN(mx)) console.log("mx IS NaN");

        this.config.mouse.currentViewPortPosition = { x: mx, y: my };
        this.config.mouse.currentCanvasPosition = { x: clientX, y: clientY };

        // We return a simple javascript object (a hash) with x and y defined
        return {
            x: mx,
            y: my,
            clientX: clientX,
            clientY: clientY,
            mouseX: e.x,
            mouseY: e.y,
            time: new Date(),
        };
    }

    setCanvas(canvas: HTMLCanvasElement | null) {
        this.canvas = canvas;

        canvas.addEventListener(
            "keydown",
            (e) => {
                this._delegate.keyDown(e);
            },
            true,
        );

        canvas.addEventListener(
            "keypress",
            (e) => {
                this._delegate.keyPress(e);
            },
            true,
        );

        canvas.addEventListener(
            "keyup",
            (e) => {
                this._delegate.keyUp(e);
            },
            true,
        );

        canvas.addEventListener(
            "mousedown",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseDown(e, this._getMouse(e));
            },
            true,
        );

        canvas.addEventListener(
            "mousemove",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseMove(e, this._getMouse(e));
            },
            true,
        );

        canvas.addEventListener(
            "mouseup",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseUp(e, this._getMouse(e));
            },
            true,
        );

        canvas.addEventListener(
            "dblclick",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseDoubleClick(e, this._getMouse(e));
            },
            true,
        );

        canvas.addEventListener(
            "mousewheel",
            (e) => {
                if (!(e instanceof MouseEvent)) return;
                this._delegate.mouseWheel(e, this._getMouse(e));

                e.preventDefault();
                return false;
            },
            true,
        );

        canvas.addEventListener(
            "touchstart",
            (e) => {
                if (!(e instanceof TouchEvent)) return;
                this._delegate.touchStart(e, this._getMouse(e));
                disableContextMenu(e);
            },
            true,
        );

        canvas.addEventListener(
            "touchmove",
            (e) => {
                if (!(e instanceof TouchEvent)) return;
                this._delegate.touchMove(e, this._getMouse(e));
                disableContextMenu(e);
            },
            true,
        );

        canvas.addEventListener(
            "touchend",
            (e) => {
                if (!(e instanceof TouchEvent)) return;
                this._delegate.touchEnd(e, this._getMouse(e));
                disableContextMenu(e);
            },
            true,
        );

        canvas.addEventListener(
            "selectstart",
            (e) => {
                //this_._delegate.mouseSelectStart(e, this_._getMouse(e));
                e.preventDefault();
                return false;
            },
            true,
        );

        canvas.addEventListener("contextmenu", disableContextMenu, true);

        this.config.canvas.windowChange
            .pipe(takeUntil(this.lifecycleEventEmitter.onDestroyEvent))
            .subscribe(() => this.updateCanvasSize());
    }

    /**
     * Draw Called by the renderer during a redraw.
     */
    draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        if (this._delegate) this._delegate.draw(ctx, zoom, pan, drawMode);
    }

    private updateCanvasSize(): void {
        const element = this.canvas;

        const width = element.clientWidth;
        const height = element.clientHeight;

        // Get padding and border values using computed style
        const computedStyle = window.getComputedStyle(element);
        const stylePaddingLeft = parseInt(computedStyle.paddingLeft) || 0;
        const stylePaddingTop = parseInt(computedStyle.paddingTop) || 0;
        const styleBorderLeft = parseInt(computedStyle.borderLeftWidth) || 0;
        const styleBorderTop = parseInt(computedStyle.borderTopWidth) || 0;

        // Get HTML element offsets
        const html = document.documentElement;
        const htmlTop = html.offsetTop;
        const htmlLeft = html.offsetLeft;

        this.mouseOffsetX = 0;
        this.mouseOffsetY = 0;

        // Compute the total offset (using native offsetParent chain traversal)
        let currentElement: HTMLElement | null = element;
        while (currentElement) {
            this.mouseOffsetX += currentElement.offsetLeft;
            this.mouseOffsetY += currentElement.offsetTop;
            currentElement = currentElement.offsetParent as HTMLElement;
        }

        // Add padding, border style widths, and HTML offsets
        this.mouseOffsetX +=
            stylePaddingLeft + styleBorderLeft + htmlLeft + width / 2;
        this.mouseOffsetY +=
            stylePaddingTop + styleBorderTop + htmlTop + height / 2;
    }
}
