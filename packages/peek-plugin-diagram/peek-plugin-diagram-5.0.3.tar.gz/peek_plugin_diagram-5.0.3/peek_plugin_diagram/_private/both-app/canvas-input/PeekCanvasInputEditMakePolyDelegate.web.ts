import {
    CanvasInputPos,
    InputDelegateConstructorViewArgs,
    PeekCanvasInputDelegate,
} from "./PeekCanvasInputDelegate.web";
import { EditorToolType } from "../canvas/PeekCanvasEditorToolType.web";
import { DispPoly } from "../canvas-shapes/DispPoly";
import { DispBaseT, DispHandleTypeE, PointI } from "../canvas-shapes/DispBase";
import { DispPolygon } from "../canvas-shapes/DispPolygon";
import {
    DispPolyline,
    DispPolylineEndTypeE,
} from "../canvas-shapes/DispPolyline";
import { DrawModeE } from "../canvas-render/PeekDispRenderDelegateABC.web";
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
export class PeekCanvasInputEditMakeDispPolyDelegate extends PeekCanvasInputDelegate {
    // Stores the rectangle being created
    protected _creating = null;

    // Used to detect dragging and its the mouse position we use
    protected _startMousePos: CanvasInputPos | null = null;
    protected _startNodeDisp = null;
    protected _endNodeDisp = null;

    protected _nodes = []; //canvasInput._scope.pageData.modelRenderables;

    protected endCreateActionHandle: PeekCanvasInputEditActionHandle | null =
        null;

    constructor(
        viewArgs: InputDelegateConstructorViewArgs,
        editArgs: InputDelegateConstructorEditArgs,
        tool: EditorToolType,
    ) {
        super(viewArgs, editArgs, tool);

        this.viewArgs.model.selection.clearSelection();
        this._reset();
    }

    _reset() {
        this._creating = null;
        this._startNodeDisp = null;
        this._endNodeDisp = null;

        // See mousedown and mousemove events for explanation
        this._startMousePos = null;
        this._lastMousePos = new CanvasInputPos();
    }

    override keyUp(event) {
        if (!this._creating) return;

        // Cancel creating object
        if (
            event.keyCode == 46 || // delete
            event.keyCode == 27
        ) {
            // escape
            this._reset();
            return;
        }

        if (event.keyCode == 8) {
            // Backspace
            // We want to keep at least two points at all times
            if (DispPoly.pointCount(this._creating) < 3) return;
            // Remove last point
            DispPoly.popPoint(this._creating);
            this.viewArgs.config.invalidate();
            return;
        }

        if (event.keyCode == 13) {
            // Enter
            this._finaliseCreate();
            return;
        }
    }

    // Map mouse events
    override mouseDown(event: MouseEvent, inputPos: CanvasInputPos) {
        this.inputStart(inputPos);
    }

    // ---------------

    override mouseMove(event: MouseEvent, inputPos: CanvasInputPos) {
        this.inputMove(inputPos, event.shiftKey);
    }

    override mouseUp(event: MouseEvent, inputPos: CanvasInputPos) {
        if (event.button == 2) {
            this._finaliseCreate();
            return;
        }
        this.inputEnd(inputPos, event.shiftKey, false);
    }

    override mouseDoubleClick(event: MouseEvent, inputPos: CanvasInputPos) {
        // The double click will cause two "MouseUp" events
        DispPoly.popPoint(this._creating);
        DispPoly.popPoint(this._creating);
        this._finaliseCreate();
    }

    // Map touch events
    override touchStart(event: TouchEvent, inputPos: CanvasInputPos) {
        if (event.touches.length == 2) {
            this._finaliseCreate();
            return;
        }

        this.inputStart(inputPos);
    }

    // ---------------

    override touchMove(event: TouchEvent, inputPos: CanvasInputPos) {
        this.inputMove(inputPos, event.shiftKey);
    }

    override touchEnd(event: TouchEvent, inputPos: CanvasInputPos) {
        this.inputEnd(inputPos, false, true);
    }

    delegateWillBeTornDown() {
        //this._finaliseCreate();
    }

    // ---------------

    override draw(
        ctx: CanvasRenderingContext2D,
        zoom: number,
        pan: PointI,
        drawMode: DrawModeE,
    ) {
        if (this.endCreateActionHandle) {
            this.endCreateActionHandle.draw(ctx);
        }
    }

    protected createDisp(inputPos: CanvasInputPos) {
        this.endCreateActionHandle = null;

        // Create the Disp
        if (this.NAME == EditorToolType.EDIT_MAKE_POLYGON)
            this._creating = DispPolygon.create(this.viewArgs.config.coordSet);
        else
            this._creating = DispPolyline.create(this.viewArgs.config.coordSet);

        if (this.NAME == EditorToolType.EDIT_MAKE_LINE_WITH_ARROW)
            DispPolyline.setEndEndType(
                this._creating,
                DispPolylineEndTypeE.Arrow,
            );

        DispPoly.addPoint(this._creating, this._startMousePos);
        this._setLastMousePos(this._startMousePos);

        DispPoly.addPoint(this._creating, inputPos);

        // Link the Disp
        this.editArgs.lookupService._linkDispLookups(this._creating);

        // Add the shape to the branch
        this._creating =
            this.editArgs.branchContext.branchTuple.addOrUpdateDisp(
                this._creating,
                true,
            );

        // TODO, Snap the coordinates if required
        // if (this.viewArgs.config.editor.snapToGrid)
        //     DispText.snap(this._creating, this.viewArgs.config.editor.snapSize);

        // Let the canvas editor know something has happened.
        // this.editArgs.dispPropsUpdated();

        this.viewArgs.model.recompileModel();

        this.viewArgs.model.selection.replaceSelection(this._creating);

        this._addBranchAnchor(inputPos.x, inputPos.y);
    }

    private endLineCreateTickCenter(fromTouch: boolean): PointI | null {
        if (!this._creating) {
            return null;
        }

        if (fromTouch) {
            if (DispPoly.pointCount(this._creating) < 2) {
                return null;
            }

            return DispPoly.lastPoint(this._creating);
        } else {
            if (DispPoly.pointCount(this._creating) < 3) {
                return null;
            }

            return DispPoly.point(
                this._creating,
                DispPoly.pointCount(this._creating) - 2,
            );
        }
    }

    private _nodeDispClickedOn(point: PointI): DispBaseT | null {
        for (let i = this._nodes.length - 1; 0 <= i; i--) {
            let disp = this._nodes[i];
            if (disp.bounds != null && disp.bounds.contains(point.x, point.y)) {
                return disp;
            }
        }

        return null;
    }

    // Start logic
    private inputStart(inputPos: CanvasInputPos) {
        /*
         if (this._startNodeDisp) {
         this._startMousePos = inputPos;
         return;
         }
         
         
         this._startNodeDisp = this._nodeDispClickedOn(inputPos);
         
         if (!this._startNodeDisp) {
         this.editArgs.balloonMsg.showWarning("A conductor must start on a node");
         this._reset();
         // this.canvasInput._scope.pageMethods.cableCreateCallback();
         return;
         }
         */
        this._lastMousePos = inputPos;
        if (!this._creating) {
            this._startMousePos = inputPos;
            this.createDisp(inputPos);
        }
    }

    protected inputMove(inputPos: CanvasInputPos, shiftKey: boolean = false) {
        if (this._startMousePos == null) return;

        const newPoint = this._coord(inputPos, shiftKey);
        DispPoly.updateLastPoint(this._creating, newPoint.x, newPoint.y);

        this.viewArgs.config.invalidate();
    }

    private inputEnd(
        inputPos: CanvasInputPos,
        shiftKey: boolean,
        fromTouch: boolean,
    ) {
        if (!this._startMousePos) return;

        if (!this._hasPassedDragThreshold(this._startMousePos, inputPos))
            return;

        if (
            this.NAME == EditorToolType.EDIT_MAKE_LINE_WITH_ARROW &&
            DispPoly.pointCount(this._creating) == 2
        ) {
            this._finaliseCreate();
        } else {
            const point = this._coord(this._lastMousePos, shiftKey);
            if (this.endCreateActionHandle?.wasClickedOn(point)) {
                if (!fromTouch) {
                    DispPoly.popPoint(this._creating);
                }
                this._finaliseCreate();
            } else {
                DispPoly.addPoint(this._creating, point);

                const endLineCreatePoint =
                    this.endLineCreateTickCenter(fromTouch);

                // Initialise the end edit action handle.
                this.endCreateActionHandle =
                    new PeekCanvasInputEditActionHandle(
                        this.viewArgs,
                        {
                            disp: this._creating,
                            center: {
                                x:
                                    endLineCreatePoint.x +
                                    this.viewArgs.config.editor
                                        .primaryEditActionHandleMargin,
                                y:
                                    endLineCreatePoint.y -
                                    this.viewArgs.config.editor
                                        .primaryEditActionHandleMargin,
                            },
                            handleType: DispHandleTypeE.primaryAction,
                        },
                        EditActionDisplayTypeE.Tick,
                        EditActionDisplayPriorityE.Success,
                        this._creating,
                    );
            }
        }

        this.viewArgs.config.invalidate();
    }

    protected _finaliseCreate() {
        this.endCreateActionHandle = null;

        if (this._creating == null) return;
        this._checkNewShapeIsVisible(this._creating);

        let poly = this._creating;
        let startNodeDisp = this._startNodeDisp;
        let endNodeDisp = null;

        this._reset();

        let lastPointCoord = DispPoly.lastPoint(poly);
        endNodeDisp = this._nodeDispClickedOn(lastPointCoord);

        if (!endNodeDisp) {
            // this.editArgs.balloonMsg.showWarning("A conductor must end on a node");
            poly = null;
        }

        // this.canvasInput._scope.pageMethods.cableCreateCallback(poly, startNodeDisp, endNodeDisp);

        this.editArgs.branchContext.branchTuple.touchUpdateDate(true);
        this.editArgs.branchContext.branchTuple.touchUndo();
        this.viewArgs.config.invalidate();
        this.editArgs.setEditorSelectTool();
    }

    protected _coord(mouse: CanvasInputPos, shiftKey: boolean = false): PointI {
        let point = { x: mouse.x, y: mouse.y };

        // When the shift key is pressed, we will align to x or y axis
        if (this._creating != null && shiftKey) {
            const lastPoint = DispPoly.point(
                this._creating,
                DispPoly.pointCount(this._creating) - 2,
            );
            const dx = Math.abs(point.x - lastPoint.x);
            const dy = Math.abs(point.y - lastPoint.y);

            if (dx > dy) point.y = lastPoint.y;
            else point.x = lastPoint.x;
        }

        // return
        return point;
    }
}
