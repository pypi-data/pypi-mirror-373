import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import {
    CanvasInputDeltaI,
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
    PeekCanvasInputDelegate,
} from "./PeekCanvasInputDelegate.web";
import { PolylineEnd } from "../canvas/PeekCanvasModelQuery.web";
import { assert } from "../DiagramUtil";
import {
    DispBase,
    DispHandleI,
    DispType,
    PointI,
} from "../canvas-shapes/DispBase";
import { DispPolyline, DispPolylineT } from "../canvas-shapes/DispPolyline";
import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { DispFactory } from "../canvas-shapes/DispFactory";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
import { DispGroupPointerT } from "../canvas-shapes/DispGroupPointer";
import { InputDelegateConstructorEditArgs } from "./PeekCanvasInputDelegateUtil.web";
import {
    EditActionDisplayPriorityE,
    EditActionDisplayTypeE,
    PeekCanvasInputEditActionHandle,
} from "./PeekCanvasInputEditActionHandle";

/**
 * This input delegate handles :
 * Zooming (touch and mouse)
 * Panning (touch and mouse)
 * Selecting at a point (touch and mouse)
 *
 */
export class PeekCanvasInputEditSelectDelegate extends PeekCanvasInputDelegate {
    static readonly TOOL_NAME = EditorToolType.EDIT_SELECT_TOOL;

    // CONSTANTS
    private readonly STATE_NONE = 0;
    private readonly STATE_SELECTING = 1;
    private readonly STATE_DRAG_SELECTING = 2;
    private readonly STATE_MOVING_DISP = 3;
    private readonly STATE_MOVING_HANDLE = 4;
    private readonly STATE_CANVAS_PANNING = 5;
    private readonly STATE_CANVAS_ZOOMING = 6;
    private readonly STATE_CANVAS_RIGHT_MOUSE_DOWN = 7;
    private readonly STATE_CANVAS_MIDDLE_MOUSE_DOWN = 8;

    private _state = 0; // STATE_NONE;
    private _passedDragThreshold: boolean = false;
    private _mouseDownOnSelection: boolean = false;
    private _mouseDownOnDisp: boolean = false;
    private _mouseDownWithShift: boolean = false;
    private _mouseDownWithCtrl: boolean = false;
    private _mouseDownMiddleButton: boolean = false;
    private _mouseDownRightButton: boolean = false;
    private _mouseDownOnHandle: DispHandleI | null = null;

    private _selectedDispsToMove: any[] = [];
    private _selectedPolylineEnds: PolylineEnd[] = [];

    private _lastPinchDist = null;

    // See mousedown and mousemove events for explanation
    private _startMousePos: CanvasInputPos | null = null;

    // The primary edit action handler
    private primaryEditActionHandle: PeekCanvasInputEditActionHandle | null =
        null;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
    ) {
        super(viewArgs, editArgs, PeekCanvasInputEditSelectDelegate.TOOL_NAME);

        this._reset();
    }

    deleteSelectedDisps() {
        const disps = this.viewArgs.model.query.decentAndAddDisps(
            this.viewArgs.model.selection.selectedDisps(),
        );
        this.viewArgs.model.selection.clearSelection();

        this.editArgs.branchContext.branchTuple.removeDisps(disps);
        this.editArgs.branchContext.branchTuple.touchUndo();
        this.viewArgs.model.recompileModel();
    }

    // ------------------------------------------------------------------------
    // Public delete method, used by the toolbar as well.

    override keyUp(event) {
        // let charCode = (typeof event.which == "number") ? event.which :
        // event.keyCode;
        // alert(charCode + "| pressed");
        let phUpDownZoomFactor = this.viewArgs.config.mouse.phUpDownZoomFactor;

        // Delete the disp on the canvas
        if (
            event.keyCode == 46 || // delete?
            event.keyCode == 8
        ) {
            // macOS "delete"
            this.deleteSelectedDisps();
        } else if (event.keyCode == 33) {
            // Page UP
            let zoom = this.viewArgs.config.viewPort.zoom;
            zoom *= 1.0 + phUpDownZoomFactor / 100.0;
            this.viewArgs.config.updateViewPortZoom(zoom);
        } else if (event.keyCode == 34) {
            // Page Down
            let zoom = this.viewArgs.config.viewPort.zoom;
            zoom *= 1.0 - phUpDownZoomFactor / 100.0;
            this.viewArgs.config.updateViewPortZoom(zoom);

            // Snap selected objects to grid
            //} else if (String.fromCharCode(event.keyCode) == "S") {
            //    this._snapSelectedCoords();
        } else if (event.keyCode == 89 && event.ctrlKey) {
            // CTRL+Y
            this.editArgs.doRedo();
        } else if (event.keyCode == 90 && event.ctrlKey) {
            // CTRL+Z
            this.editArgs.doUndo();
        } else if (event.keyCode == 67 && event.ctrlKey) {
            // CTRL+C
            this.viewArgs.copyPasteService.doCopy();
            // this.editArgs.doCopy();
        } else if (event.keyCode == 86 && event.ctrlKey) {
            // CTRL+V
            this.viewArgs.copyPasteService.doPaste();
        }
    }

    // ------------------------------------------------------------------------
    // Input handlers

    override touchStart(event: TouchEvent, inputPos: CanvasInputPos) {
        if (event.targetTouches.length == 2) {
            this._state = this.STATE_CANVAS_ZOOMING;
            this._lastPinchDist = null;
        } else {
            this.mouseDown(event, inputPos);
        }
    }

    // fixes a problem where double clicking causes
    // text to get selected on the canvas
    // mouseSelectStart (event,
    // mouse) {
    // };

    override mouseDown(event, inputPos: CanvasInputPos) {
        this._mouseDownWithShift = event.shiftKey;
        this._mouseDownWithCtrl = event.ctrlKey;
        this._mouseDownMiddleButton = event.button == 1;
        this._mouseDownRightButton = event.button == 2;
        this._startMousePos = inputPos;
        this._lastMousePos = inputPos;

        if (this._mouseDownRightButton) {
            this._state = this.STATE_CANVAS_RIGHT_MOUSE_DOWN;
            return;
        }

        if (this._mouseDownMiddleButton) {
            this._state = this.STATE_CANVAS_MIDDLE_MOUSE_DOWN;
            return;
        }

        const q = this.viewArgs.model.query;

        let visibleDisps = q.filterForVisibleDisps(
            this.viewArgs.model.query.editableShapes,
            this.viewArgs.config.viewPort.zoom,
            true,
            true,
        );

        let selectedDisps = this.viewArgs.model.selection.selectedDisps();
        let margin =
            this.viewArgs.config.mouse.selecting.margin /
            this.viewArgs.config.viewPort.zoom;

        // Handles are only shown when one item is selected
        if (selectedDisps.length == 1) {
            let disp = selectedDisps[0];
            let handles = this.viewArgs.renderFactory.handles(
                disp,
                this.viewArgs.config.viewPort.zoom,
            );
            for (let j = 0; j < handles.length; j++) {
                let handle = handles[j];
                if (handle.box.contains(inputPos.x, inputPos.y, margin)) {
                    this._mouseDownOnHandle = handle;
                    break;
                }
            }
        }

        // Have they clicked on the primary edit function handle?
        if (
            this.primaryEditActionHandle?.wasClickedOn({
                x: inputPos.x,
                y: inputPos.y,
            })
        ) {
            this.callHandlePrimaryAction(
                this.primaryEditActionHandle.shape,
                inputPos,
            );
            return;
        }

        for (let i = selectedDisps.length - 1; i >= 0; i--) {
            let d = selectedDisps[i];
            if (d.bounds && d.bounds.contains(inputPos.x, inputPos.y, margin)) {
                this._mouseDownOnSelection = true;
                break;
            }
        }

        if (this._mouseDownOnSelection) {
            this._mouseDownOnDisp = true;
        } else {
            for (let i = visibleDisps.length - 1; i >= 0; i--) {
                let d = visibleDisps[i];
                if (
                    d.bounds &&
                    d.bounds.contains(inputPos.x, inputPos.y, margin)
                ) {
                    this._mouseDownOnDisp = true;
                    break;
                }
            }
        }

        if (this._mouseDownOnHandle != null) {
            this.startStateMovingHandle(inputPos);
        } else if (this._mouseDownOnDisp) {
            this._state = this.STATE_SELECTING;
        } else {
            this._state = this.STATE_SELECTING;
            this.viewArgs.model.selection.clearSelection();
        }
    }

    override touchMove(event: TouchEvent, inputPos: CanvasInputPos) {
        if (this._state == this.STATE_CANVAS_ZOOMING) {
            this._touchZoom(event, inputPos);
        } else {
            this.mouseMove(event, inputPos);
        }

        event.preventDefault();
    }

    override mouseMove(event, inputPos: CanvasInputPos) {
        if (this._state == this.STATE_NONE) return;

        this._passedDragThreshold =
            this._passedDragThreshold ||
            this._hasPassedDragThreshold(this._startMousePos, inputPos);

        // State conversion upon dragging
        if (
            this._state == this.STATE_CANVAS_RIGHT_MOUSE_DOWN ||
            this._state == this.STATE_CANVAS_MIDDLE_MOUSE_DOWN
        ) {
            if (this._passedDragThreshold) {
                this._state = this.STATE_CANVAS_PANNING;
            } else {
                return;
            }
        }

        // State conversion upon dragging
        if (this._state == this.STATE_SELECTING && this._passedDragThreshold) {
            if (this._mouseDownOnSelection) {
                this.startStateMovingDisp(inputPos);
            } else if (this._mouseDownOnDisp) {
                this._changeSelection(this._selectByPoint(this._startMousePos));
                this.startStateMovingDisp(inputPos);
            } else {
                this._state = this.STATE_DRAG_SELECTING;
            }
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

            case this.STATE_DRAG_SELECTING: {
                this._lastMousePos = inputPos;
                break;
            }

            case this.STATE_MOVING_DISP: {
                let delta = this._setLastMousePos(inputPos);
                this.deltaMoveSelection(delta);
                break;
            }

            case this.STATE_MOVING_HANDLE: {
                let delta = this._setLastMousePos(inputPos);

                const h = this._mouseDownOnHandle;
                if (
                    DispPolyline.isStartHandle(h.disp, h.handleIndex) ||
                    DispPolyline.isEndHandle(h.disp, h.handleIndex)
                ) {
                    this.deltaMoveSelection(delta);
                } else {
                    this.deltaMoveHandle(delta);
                }
                break;
            }
        }

        this.viewArgs.config.invalidate();
    }

    override touchEnd(event: TouchEvent, mouse) {
        this.mouseUp(event, mouse);
    }

    override mouseUp(event, inputPos: CanvasInputPos) {
        // Store the change
        switch (this._state) {
            case this.STATE_SELECTING:
            case this.STATE_DRAG_SELECTING: {
                // Handle selection change
                let hits = [];
                if (this._state == this.STATE_SELECTING) {
                    hits = this._selectByPoint(this._startMousePos);
                } else if (this._state == this.STATE_DRAG_SELECTING) {
                    hits = this._selectByBox(this._startMousePos, inputPos);
                } else {
                    assert(false, "Invalid state");
                }

                this._changeSelection(hits);
                break;
            }

            case this.STATE_MOVING_DISP: {
                this.finishStateMovingDisp();
                break;
            }

            case this.STATE_MOVING_HANDLE: {
                this.finishStateMovingHandle();
                break;
            }

            case this.STATE_CANVAS_RIGHT_MOUSE_DOWN: {
                if (this._mouseDownRightButton) {
                    this.viewArgs.contextMenuService.doOpenMenu(event);
                }
                break;
            }
        }

        this._reset();
        this.viewArgs.config.invalidate();
    }

    override mouseDoubleClick(event, inputPos: CanvasInputPos) {
        // If the mouse was down on a action handle, then handle that
        if (
            this.primaryEditActionHandle?.wasClickedOn({
                x: inputPos.x,
                y: inputPos.y,
            })
        ) {
            this.callHandlePrimaryAction(
                this.primaryEditActionHandle.shape,
                inputPos,
            );
            return;
        }

        const hits = this._selectByPoint(inputPos);
        if (hits.length === 1) {
            this._changeSelection(hits);
            this._state == this.STATE_NONE;

            this.callHandlePrimaryAction(hits[0], inputPos);
        }
    }

    override mouseWheel(event, inputPos: CanvasInputPos) {
        let delta = event.deltaY || event.wheelDelta;

        // Overcome windows zoom multipliers
        if (15 < delta) delta = 15;

        if (delta < -15) delta = -15;

        this._zoomPan(inputPos.clientX, inputPos.clientY, delta);
    }

    override draw(ctx, zoom: number, pan: PointI, drawMode: DrawModeE) {
        this.resetPrimaryActionHandle();

        switch (this._state) {
            case this.STATE_DRAG_SELECTING: {
                let zoom = this.viewArgs.config.viewPort.zoom;
                let x = this._startMousePos.x;
                let y = this._startMousePos.y;
                let w = this._lastMousePos.x - this._startMousePos.x;
                let h = this._lastMousePos.y - this._startMousePos.y;

                ctx.strokeStyle = this.viewArgs.config.mouse.selecting.color;
                ctx.lineWidth =
                    this.viewArgs.config.mouse.selecting.width / zoom;
                ctx.dashedRect(
                    x,
                    y,
                    w,
                    h,
                    this.viewArgs.config.mouse.selecting.dashLen / zoom,
                );
                ctx.stroke();
                break;
            }

            case this.STATE_NONE: {
                // Draw the primary edit action if it exists
                this.primaryEditActionHandle?.draw(ctx);
                break;
            }
        }
    }

    private _reset() {
        // **** Keep track of state! ****
        this._state = this.STATE_NONE;
        this._passedDragThreshold = false;
        this._mouseDownOnSelection = false;
        this._mouseDownOnDisp = false;
        this._mouseDownWithShift = false;
        this._mouseDownWithCtrl = false;
        this._mouseDownMiddleButton = false;
        this._mouseDownRightButton = false;
        this._mouseDownOnHandle = null;

        this._lastPinchDist = null;

        // See mousedown and mousemove events for explanation
        this._startMousePos = null;
        this._lastMousePos = null;
    }

    private _touchZoom(event, inputPos: CanvasInputPos) {
        let t1x = event.targetTouches[0].pageX;
        let t1y = event.targetTouches[0].pageY;
        let t2x = event.targetTouches[1].pageX;
        let t2y = event.targetTouches[1].pageY;

        // Get the center coordinate, Average
        let center = {
            clientX: inputPos.clientX,
            clientY: inputPos.clientY,
        };
        console.log(center);

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

    private _zoomPan(clientX, clientY, delta) {
        if (!delta) {
            return;
        }

        delta = delta * -1; // Correct the zooming to match google maps, etc

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

    // ------------------------------------------------------------------------
    // Methods for changing to the move states

    private startStateMovingHandle(inputPos: CanvasInputPos) {
        this._state = this.STATE_MOVING_HANDLE;

        const h = this._mouseDownOnHandle;
        if (DispBase.typeOf(h.disp) == DispType.groupPointer) {
            this.prepareDispGroupHandleRotate();
        } else if (
            DispPolyline.isStartHandle(h.disp, h.handleIndex) ||
            DispPolyline.isEndHandle(h.disp, h.handleIndex)
        ) {
            this.prepareDispPolyHandleMove();
        }

        this.addDispsToBranchForUpdate(inputPos);

        // When the above method copies the object the handle is for,
        // we need to update the handle.
        const selection = this.viewArgs.model.selection.selectedDisps();
        if (selection.length != 0) h.disp = selection[0];
    }

    private finishStateMovingHandle() {
        this.editArgs.branchContext.branchTuple.touchUndo();
    }

    private startStateMovingDisp(inputPos: CanvasInputPos) {
        this._state = this.STATE_MOVING_DISP;
        this.prepareSelectionForMove();
        this.addDispsToBranchForUpdate(inputPos);
    }

    private finishStateMovingDisp() {
        this.editArgs.branchContext.branchTuple.touchUndo();
    }

    // ------------------------------------------------------------------------
    // Methods for finding the disps

    private _selectByPoint(inputPos: CanvasInputPos) {
        const q = this.viewArgs.model.query;

        let disps = this.viewArgs.model.query.editableShapes;

        // Filter out disps that are apart of a group
        // Filter out null shapes, we don't allow editing of those any more
        disps = disps.filter(
            (d) =>
                DispBase.groupId(d) == null &&
                DispBase.typeOf(d) != DispType.null_,
        );

        // Filter for shapes that contain the point.
        let hits = q.filterForDispsContainingPoint(
            disps,
            this.viewArgs.config.viewPort.zoom,
            this.viewArgs.config.mouse.selecting.margin,
            inputPos,
            false,
        );

        // Sort by how close the click is from the center of the box.
        hits = q.sortByDistanceFromCenter(hits, inputPos);

        // Only select
        if (!this._mouseDownWithCtrl && hits.length) {
            hits = [hits[0]];
        }

        return hits;
    }

    private _selectByBox(inputPos1: CanvasInputPos, inputPos2: CanvasInputPos) {
        // Get all shapes.
        let disps = this.viewArgs.model.query.editableShapes;

        // Filter out disps that are apart of a group
        disps = disps.filter((d) => DispBase.groupId(d) == null);

        let b = PeekCanvasBounds.fromPoints([inputPos1, inputPos2]);

        return disps.filter(
            (d) => d.bounds && d.bounds.withIn(b.x, b.y, b.w, b.h),
        );
    }

    /*
     // This method was used to select all disps of the same color/size, etc
     private _selectByTypeAndBounds(inputPos: CanvasInputPos) {
     
     let hits = this._selectByPoint(inputPos);
     if (!hits.length)
     return [];
     
     let masterCoord = hits[hits.length - 1];
     let disps = this.viewArgs.model.query.editableShapes;
     
     return disps.filter(d => d.bounds && d.bounds.similarTo(masterCoord));
     }
     */

    private _changeSelection(hits) {
        // Remove clicked on thing
        if (this._mouseDownOnSelection && this._mouseDownWithShift) {
            this.viewArgs.model.selection.removeSelection(hits);
        } else {
            // Remove all previous selection
            if (this._mouseDownWithShift)
                this.viewArgs.model.selection.addSelection(hits);
            else this.viewArgs.model.selection.replaceSelection(hits);
        }

        for (const disp of this.viewArgs.model.selection.selectedDisps()) {
            DispFactory.wrapper(disp).resetMoveData(disp);
            // console.log(disp);
        }
    }

    private callHandlePrimaryAction(disp, inputPos: CanvasInputPos): void {
        this.editArgs?.editPrimaryActionFactory
            .handlePrimaryAction(disp, inputPos)
            .then(() => {});
    }

    private resetPrimaryActionHandle(): void {
        const selectedDisps = this.viewArgs.model.selection.selectedDisps();

        this.primaryEditActionHandle = null;
        if ((selectedDisps?.length || 0) !== 1) {
            return;
        }

        const selectedDisp = selectedDisps[0];
        const Wrapper = DispFactory.wrapper(selectedDisp);
        const primaryEditHandle = Wrapper.primaryActionHandlePoint(
            selectedDisp,
            this.viewArgs.config.editor.primaryEditActionHandleMargin /
                this.viewArgs.config.viewPort.zoom,
        );

        if (primaryEditHandle == null) {
            return null;
        }

        this.primaryEditActionHandle = new PeekCanvasInputEditActionHandle(
            this.viewArgs,
            primaryEditHandle,
            EditActionDisplayTypeE.Pencil,
            EditActionDisplayPriorityE.Default,
            selectedDisp,
        );
    }

    // ------------------------------------------------------------------------
    // Methods for setting the selection based on hits

    private prepareDispPolyHandleMove() {
        this._selectedDispsToMove = [];
        this._selectedPolylineEnds = [];

        const h = this._mouseDownOnHandle;

        let key = null;
        let point = null;

        if (DispPolyline.isStartHandle(h.disp, h.handleIndex)) {
            key = DispPolyline.startKey(<DispPolylineT>h.disp);
            point = DispPolyline.firstPoint(<DispPolylineT>h.disp);
        } else {
            // It must be the end
            key = DispPolyline.endKey(<DispPolylineT>h.disp);
            point = DispPolyline.lastPoint(<DispPolylineT>h.disp);
        }

        // We need to
        // 1) Add all the shapes that have a matching key
        // 2) Add all shapes in the groups of those shapes
        // 3) Add all the ends that have keys matching keys of any of the shapes so far
        // 4) Add all the ends that land on the same point.

        const q = this.viewArgs.model.query;

        // Get all the shapes for the starting key
        let disps = [];

        if (key) disps = q.dispsForKeys([key]);

        // Get all disps in the groups that we're moving
        disps = q.uniqueDisps(disps.add(q.dispsForGroups(disps.slice())));
        this._selectedDispsToMove = disps;

        // Get all the polyline ends that land of the keys we're moving
        let ends = q.polylinesConnectedToDispKey(q.keyOfDisps(disps));
        ends.add(q.polylinesConnectedToPoint([point]));

        this._selectedPolylineEnds = q.uniquePolylineEnds(ends);
    }

    private prepareDispGroupHandleRotate() {
        this._selectedDispsToMove = [];
        this._selectedPolylineEnds = [];

        const h = this._mouseDownOnHandle;

        assert(
            DispBase.typeOf(h.disp) == DispType.groupPointer,
            "DispGroupPtr not provided",
        );

        this._selectedDispsToMove = this.viewArgs.model.query.decentAndAddDisps(
            (<DispGroupPointerT>h.disp).disps,
        );
    }

    private prepareSelectionForMove() {
        this._selectedDispsToMove = [];
        this._selectedPolylineEnds = [];
        const q = this.viewArgs.model.query;

        // Lookup of IDs that are the polylines we're moving
        const polylineIds = {};

        // All the disps with the same key
        let disps: any[] = q.dispsForKeys(
            q.keyOfDisps(this.viewArgs.model.selection.selectedDisps()),
        );

        // all the disps that have matching keys
        disps.add(this.viewArgs.model.selection.selectedDisps());

        // Filter out the duplicates
        disps = q.uniqueDisps(disps);

        // List of all the keys being moved
        let polylineEndKeys = [];

        // Create a list of all the keys we're moving
        for (let disp of disps) {
            if (DispBase.typeOf(disp) == DispType.polyline) {
                polylineIds[DispBase.id(disp)] = true;
                polylineEndKeys.push(DispPolyline.startKey(disp));
                polylineEndKeys.push(DispPolyline.endKey(disp));
            }
        }
        // filter out nulls
        polylineEndKeys = polylineEndKeys.filter((k) => k != null);

        // Now get all the disps we're moving at the end of the polylines
        disps.add(q.dispsForKeys(polylineEndKeys));

        // Get all the groups for the disps we're moving
        disps = q.uniqueDisps(disps.add(q.dispsForGroups(disps.slice())));
        this._selectedDispsToMove = disps;

        // We want to include all disp keys and each end of all polylines we're moving
        polylineEndKeys.add(q.keyOfDisps(disps));
        // Get all the polyline ends that land of the keys we're moving
        // Filter out the polylines we're moving in full
        this._selectedPolylineEnds = q
            .polylinesConnectedToDispKey(polylineEndKeys)
            .filter((e) => !polylineIds[DispBase.id(e.disp)]);
    }

    /** Add Disps To Branch For Update
     *
     * For all the selected items, add them to the branch so we can use them for
     * an update.
     *
     * @param inputPos: The position of the input, used to create anchor points
     */
    private addDispsToBranchForUpdate(inputPos: CanvasInputPos) {
        // If there are no disps to move, then return here
        if (
            !this._selectedDispsToMove.length &&
            !this._selectedPolylineEnds.length
        )
            return;

        let primarySelections = this.viewArgs.model.selection.selectedDisps();
        let groupSelections = this._selectedDispsToMove;

        primarySelections =
            this.editArgs.branchContext.branchTuple.addOrUpdateDisps(
                primarySelections,
                true,
            );

        groupSelections =
            this.editArgs.branchContext.branchTuple.addOrUpdateDisps(
                groupSelections,
                true,
            );

        for (let dispPolylineEnd of this._selectedPolylineEnds) {
            dispPolylineEnd.disp =
                this.editArgs.branchContext.branchTuple.addOrUpdateDisp(
                    dispPolylineEnd.disp,
                    true,
                );
        }

        this.viewArgs.model.recompileModel();
        this.viewArgs.model.selection.replaceSelection(primarySelections);
        this._selectedDispsToMove = groupSelections;

        this._addBranchAnchor(inputPos.x, inputPos.y);
    }

    // ------------------------------------------------------------------------
    // Methods moving the selection

    private deltaMoveSelection(delta: CanvasInputDeltaI): void {
        // Move all of the shapes that are moved in full
        for (let disp of this._selectedDispsToMove) {
            DispBase.deltaMove(disp, delta.dx, delta.dy);
        }

        // Move all of the connected polyline ends
        for (let dispPolylineEnd of this._selectedPolylineEnds) {
            if (dispPolylineEnd.isStart) {
                DispPolyline.deltaMoveStart(
                    dispPolylineEnd.disp,
                    delta.dx,
                    delta.dy,
                );
            } else {
                DispPolyline.deltaMoveEnd(
                    dispPolylineEnd.disp,
                    delta.dx,
                    delta.dy,
                );
            }
        }

        this.editArgs.branchContext.branchTuple.touchUpdateDate(false);
        this.viewArgs.config.invalidate();
    }

    /** Delta Move Handle
     *
     * This method is used to move all handles, EXCEPT Polyline ends
     */
    private deltaMoveHandle(delta: CanvasInputDeltaI): void {
        let handle = this._mouseDownOnHandle;
        DispFactory.wrapper(handle.disp).deltaMoveHandle(
            handle,
            delta.dx,
            delta.dy,
        );

        this.editArgs.branchContext.branchTuple.touchUpdateDate(false);
        this.viewArgs.config.invalidate();
    }
}
