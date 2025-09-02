import {
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
    PeekCanvasInputDelegate,
} from "./PeekCanvasInputDelegate.web";
import { assert } from "../DiagramUtil";
import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { DispBase, DispBaseT, PointI } from "../canvas-shapes/DispBase";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";
import { diagramPluginName } from "@peek/peek_plugin_diagram/_private/PluginNames";
import { DocDbPopupTypeE } from "@peek/peek_core_docdb";
import { DispFactory } from "../canvas-shapes/DispFactory";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputSelectDelegate extends PeekCanvasInputDelegate {
    static readonly TOOL_NAME = EditorToolType.SELECT_TOOL;

    // CONSTANTS
    STATE_NONE = 0;
    STATE_SELECTING = 1;
    STATE_CANVAS_PANNING = 5;
    STATE_CANVAS_ZOOMING = 6;

    _state = 0; // STATE_NONE;
    _passedDragThreshold = false;
    _mouseDownOnSelection = false;
    _mouseDownOnCoord = false;
    _mouseDownWithShift = false;
    _mouseDownWithCtrl = false;
    _mouseDownMiddleButton = false;
    _mouseDownRightButton = false;
    _mouseDownOnHandle = null;

    _lastPinchDist = null;

    // See mousedown and mousemove events for explanation
    _startMousePos: CanvasInputPos | null = null;

    // This is the disp that is shown when you hover over it.
    private suggestedDispToSelect: DispBaseT | null = null;

    // Used to delay the opening of the docdb popup on hover events
    private popupTimeout: any;
    private popupOpened: boolean;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(viewArgs, editArgs, PeekCanvasInputSelectDelegate.TOOL_NAME);

        this._reset();
    }

    _reset() {
        // **** Keep track of state! ****
        this._state = this.STATE_NONE;
        this._passedDragThreshold = false;
        this._mouseDownOnSelection = false;
        this._mouseDownOnCoord = false;
        this._mouseDownWithShift = false;
        this._mouseDownWithCtrl = false;
        this._mouseDownMiddleButton = false;
        this._mouseDownRightButton = false;
        this._mouseDownOnHandle = null;

        this.suggestedDispToSelect = null;

        this._lastPinchDist = null;

        // See mousedown and mousemove events for explanation
        this._startMousePos = null;
        this._lastMousePos = null;
    }

    override keyUp(event) {
        let phUpDownZoomFactor = this.viewArgs.config.mouse.phUpDownZoomFactor;

        // Page Up
        if (event.keyCode == 33) {
            let zoom = this.viewArgs.config.viewPort.zoom;
            zoom *= 1.0 + phUpDownZoomFactor / 100.0;
            this.viewArgs.config.updateViewPortZoom(zoom);
        }
        // Page Down
        else if (event.keyCode == 34) {
            let zoom = this.viewArgs.config.viewPort.zoom;
            zoom *= 1.0 - phUpDownZoomFactor / 100.0;
            this.viewArgs.config.updateViewPortZoom(zoom);
        }
    }

    // fixes a problem where double clicking causes
    // text to get selected on the canvas
    // mouseSelectStart (event,
    // mouse) {
    // }

    override touchStart(event: TouchEvent, mouse) {
        this.clearPopupTimeout();
        if (event.targetTouches.length == 2) {
            this._state = this.STATE_CANVAS_ZOOMING;
            this._lastPinchDist = null;
        } else {
            this.mouseDown(event, mouse);
        }
    }

    override mouseDown(event, mouse: CanvasInputPos) {
        this.clearPopupTimeout();
        this.suggestedDispToSelect = null;
        this._mouseDownWithShift = event.shiftKey;
        this._mouseDownWithCtrl = event.ctrlKey;
        this._mouseDownMiddleButton = event.button == 1;
        this._mouseDownRightButton = event.button == 2;
        this._startMousePos = mouse;
        this._lastMousePos = mouse;

        if (this._mouseDownMiddleButton || this._mouseDownRightButton) {
            this._state = this.STATE_CANVAS_PANNING;
            return;
        }

        let selectedDisps = this.viewArgs.model.selection.selectedDisps();

        let margin = this.viewArgs.config.mouse.selecting.margin; // * this.viewArgs.config.viewPort.zoom;

        for (let i = selectedDisps.length - 1; i >= 0; i--) {
            let d = selectedDisps[i];
            if (d.bounds && d.bounds.contains(mouse.x, mouse.y, margin)) {
                this._mouseDownOnSelection = true;
                break;
            }
        }

        if (this._mouseDownOnSelection) {
            this._mouseDownOnCoord = true;
        } else {
            let disps = this.viewArgs.model.query.selectableDisps;
            for (let i = disps.length - 1; i >= 0; i--) {
                let d = disps[i];
                if (d.bounds && d.bounds.contains(mouse.x, mouse.y, margin)) {
                    this._mouseDownOnCoord = true;
                    break;
                }
            }
        }

        if (this._mouseDownOnCoord) {
            this._state = this.STATE_SELECTING;
        } else {
            this._state = this.STATE_CANVAS_PANNING;
            this._changeSelection([], event);
        }
    }

    override touchMove(event: TouchEvent, mouse: CanvasInputPos) {
        if (this._state == this.STATE_CANVAS_ZOOMING) {
            this._touchZoom(event, mouse);
        } else {
            this.mouseMove(event, mouse);
        }
        event.preventDefault();
    }

    _touchZoom(event, mouse) {
        let t1x = event.targetTouches[0].pageX;
        let t1y = event.targetTouches[0].pageY;
        let t2x = event.targetTouches[1].pageX;
        let t2y = event.targetTouches[1].pageY;

        // Get the center coordinate, Average
        let center = {
            clientX: mouse.clientX,
            clientY: mouse.clientY,
        };

        let dist = Math.sqrt(
            (t1x - t2x) * (t1x - t2x) + (t1y - t2y) * (t1y - t2y),
        );

        if (this._lastPinchDist == null) {
            this._lastPinchDist = dist;
            return;
        }

        let delta = this._lastPinchDist - dist;
        this._lastPinchDist = dist;

        // Begin applying zoom / pan
        this._zoomPan(center.clientX, center.clientY, delta);
    }

    _zoomPan(clientX, clientY, delta) {
        if (!delta) {
            return;
        }
        this.clearPopupTimeout();
        this.clearSelectableUnderMouse();

        // Correct the zooming to match google maps, etc
        delta = delta * -1;

        // begin
        let zoom = this.viewArgs.config.viewPort.zoom;
        let pan = this.viewArgs.config.viewPort.pan;

        // The PAN is always dead center of the view port.
        // The clientX/clientY are screen pixels relative to the center of the canvas

        // Capture the initial canvas relative position
        let panStart = {
            x: clientX / zoom + pan.x,
            y: clientY / zoom + pan.y,
        };

        // Apply Zoom Delta
        zoom *= 1.0 + delta / 100.0;

        // If the zoom won't apply just exit
        if (
            !(
                this.viewArgs.config.viewPort.minZoom < zoom &&
                zoom < this.viewArgs.config.viewPort.maxZoom
            )
        ) {
            return;
        }

        // Capture the final canvas relative position
        let panEnd = {
            x: clientX / zoom + pan.x,
            y: clientY / zoom + pan.y,
        };

        let newPan = {
            x: pan.x + (panStart.x - panEnd.x),
            y: pan.y + (panStart.y - panEnd.y),
        };

        this.viewArgs.config.updateViewPortPan(newPan);
        this.viewArgs.config.updateViewPortZoom(zoom);
    }

    override mouseMove(event, inputPos: CanvasInputPos) {
        if (this._state == this.STATE_NONE) {
            this.renderSelectablesUnderMouse(inputPos, event);
            return;
        }

        this._passedDragThreshold =
            this._passedDragThreshold ||
            this._hasPassedDragThreshold(this._startMousePos, inputPos);

        // State conversion upon dragging
        if (this._state == this.STATE_SELECTING && this._passedDragThreshold) {
            this._state = this.STATE_CANVAS_PANNING;
        }

        switch (this._state) {
            case this.STATE_CANVAS_PANNING: {
                let delta = this._setLastMousePos(inputPos, false);
                // Dragging the mouse left makes a negative delta, we increase X
                // Dragging the mouse up makes a negative delta, we increase Y
                let oldPan = this.viewArgs.config.viewPort.pan;
                let newPan = {
                    x:
                        oldPan.x -
                        delta.dClientX / this.viewArgs.config.viewPort.zoom,
                    y:
                        oldPan.y -
                        delta.dClientY / this.viewArgs.config.viewPort.zoom,
                };
                this.viewArgs.config.updateViewPortPan(newPan);
                break;
            }
        }

        this.viewArgs.config.invalidate();
    }

    override touchEnd(event: TouchEvent, mouse) {
        this.mouseUp(event, mouse);
    }

    override mouseUp(event, mouse) {
        // Store the change
        switch (this._state) {
            case this.STATE_SELECTING: {
                let hits = [];
                if (this._state == this.STATE_SELECTING) {
                    hits = this._selectByPoint(this._startMousePos);
                } else {
                    assert(false, "Invalid state");
                }
                this._changeSelection(hits, event);
                break;
            }
        }

        this._reset();
        this.viewArgs.config.invalidate();
    }

    override mouseDoubleClick(event, mouse) {
        // JJC, I wrote this but never enabled it.
        // In testing, i found the docdb poping up interfears with the
        // double click
        /*        const hits = this._selectByPoint(mouse);
                if (hits.length == 0) {
                    return;
                }

                const hit = hits[0];
                const key = DispBase.key(hit);
                if (key == null) {
                    return;
                }

                this.viewArgs.objectPopupService.hideAllPopups();
                event.preventDefault();

                this.viewArgs.positionService.positionByKey(
                    this.viewArgs.config.controller.modelSetKey,
                    null,
                    { highlightKey: key },
                );

         */
    }

    override mouseWheel(event, mouse) {
        let delta = event.deltaY || event.wheelDelta;

        // Overcome windows zoom multipliers
        if (15 < delta) {
            delta = 15;
        }
        if (delta < -15) {
            delta = -15;
        }

        this._zoomPan(mouse.clientX, mouse.clientY, delta);
    }

    override draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        if (this.suggestedDispToSelect != null) {
            this.viewArgs.renderFactory.drawSelected(
                this.suggestedDispToSelect,
                ctx,
                zoom,
                pan,
                DrawModeE.ForSuggestion,
            );
        }
    }

    _selectByPoint(inputPos: CanvasInputPos) {
        const q = this.viewArgs.model.query;

        let disps = q.filterForVisibleDisps(
            q.selectableDisps,
            this.viewArgs.config.viewPort.zoom,
            true,
            false,
        );

        let hits = q.filterForDispsContainingPoint(
            disps,
            this.viewArgs.config.viewPort.zoom,
            this.viewArgs.config.mouse.selecting.margin,
            inputPos,
            true,
        );

        // Sort by how close the click is from the center of the box.
        hits = q.sortByDistanceFromCenter(hits, inputPos);

        // Only select
        if (!this._mouseDownWithCtrl && hits.length) {
            hits = [hits[0]];
        }

        return hits;
    }

    _changeSelection(hits, mouse: MouseEvent) {
        this.clearSelectableUnderMouse();

        if (hits.length == 1 && this.viewArgs.actioner.hasAction(hits[0])) {
            this.viewArgs.actioner.applyAction(hits[0]);
            return;
        }

        // If nothing is selected, clear the selection
        if (hits.length == 0) {
            this.viewArgs.model.selection.clearSelection();
            // Remove clicked on thing
        } else if (this._mouseDownOnSelection && this._mouseDownWithShift) {
            this.viewArgs.model.selection.removeSelection(hits);
        } else {
            if (this._mouseDownWithShift) {
                this.viewArgs.model.selection.addSelection(hits);
            } else {
                this.viewArgs.model.selection.replaceSelection(hits);
            }
        }

        const hit = hits[0];

        if (hit != null && DispBase.key(hit) != null) {
            // Show the tooltip
            this.viewArgs.objectPopupService.showPopup(
                true,
                DocDbPopupTypeE.summaryPopup,
                diagramPluginName,
                mouse,
                this.viewArgs.config.controller.modelSetKey,
                DispBase.key(hit),
                {
                    triggeredForContext: this.viewArgs.config.coordSet.key,
                    triggeredFromPosition: DispFactory.wrapper(hit).center(hit),
                },
            );
        }
    }

    private getUnderMouseHits(inputPos: CanvasInputPos) {
        const query = this.viewArgs.model.query;

        let disps = query.filterForVisibleDisps(
            query.selectableDisps,
            this.viewArgs.config.viewPort.zoom,
            true,
            false,
        );

        let hits = query.filterForDispsContainingPoint(
            disps,
            this.viewArgs.config.viewPort.zoom,
            this.viewArgs.config.mouse.selecting.margin,
            inputPos,
            true,
        );

        hits = query.sortByDistanceFromCenter(hits, inputPos);

        return hits;
    }

    private renderSelectablesUnderMouse(
        inputPos: CanvasInputPos,
        mouse: MouseEvent,
    ): void {
        const query = this.viewArgs.model.query;

        const hits = this.getUnderMouseHits(inputPos);

        if (!hits.length) {
            this.clearPopupTimeout();
            this.viewArgs.objectPopupService.hideHoverPopup();
            this.clearSelectableUnderMouse();
            return;
        }

        // Don't highlight already selected disps
        for (const selDisp of query.selectedDisps) {
            if (DispBase.id(selDisp) == DispBase.id(hits[0])) {
                this.clearSelectableUnderMouse();
                return;
            }
        }
        const newHit = hits[0];
        console.log(`Selected shape with id ${newHit["id"]}`);
        this.popupTooltip(newHit, mouse);

        if (
            this.suggestedDispToSelect != null &&
            DispBase.id(newHit) == DispBase.id(this.suggestedDispToSelect)
        ) {
            return;
        }

        this.popupOpened = false;
        this.clearSelectableUnderMouse();
        this.suggestedDispToSelect = newHit;
        this.viewArgs.config.invalidate();
    }

    private popupTooltip(newHit, mouse: MouseEvent) {
        if (this.popupOpened) {
            return;
        }

        if (DispBase.key(newHit) == null) {
            return;
        }

        this.clearPopupTimeout();
        this.popupTimeout = setTimeout(() => {
            if (this.popupTimeout == null) {
                return;
            }

            this.popupOpened = true;

            this.viewArgs.objectPopupService.showPopup(
                false,
                DocDbPopupTypeE.tooltipPopup,
                diagramPluginName,
                mouse,
                this.viewArgs.config.controller.modelSetKey,
                DispBase.key(newHit),
                {
                    triggeredForContext: this.viewArgs.config.coordSet.key,
                    triggeredFromPosition:
                        DispFactory.wrapper(newHit).center(newHit),
                },
            );
        }, 250);
    }

    private clearPopupTimeout(): void {
        if (this.popupTimeout != null) {
            clearTimeout(this.popupTimeout);
        }
        this.popupTimeout = null;
        this.viewArgs.objectPopupService.hideHoverPopup();
    }

    private clearSelectableUnderMouse(): void {
        this.suggestedDispToSelect = null;
        this.viewArgs.config.invalidate();
    }
}
