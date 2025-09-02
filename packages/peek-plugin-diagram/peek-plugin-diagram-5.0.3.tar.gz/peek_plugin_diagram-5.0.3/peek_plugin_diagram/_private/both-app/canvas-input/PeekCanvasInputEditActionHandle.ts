import { DispBaseT, DispHandleI, PointI } from "../canvas-shapes/DispBase";
import { PeekCanvasBounds } from "@peek/peek_plugin_diagram/_private/PeekCanvasBounds";
import { InputDelegateConstructorViewArgs } from "./PeekCanvasInputDelegateUtil.web";

export enum EditActionDisplayTypeE {
    Tick,
    Pencil,
}

export enum EditActionDisplayPriorityE {
    Success,
    Default,
}

export class PeekCanvasInputEditActionHandle {
    private point: PointI;

    constructor(
        private viewArgs: InputDelegateConstructorViewArgs,
        private handle: DispHandleI,
        private actionDisplayType: EditActionDisplayTypeE,
        private actionDisplayPriorityType: EditActionDisplayPriorityE = EditActionDisplayPriorityE.Success,
        public readonly shape: DispBaseT,
    ) {
        this.point = handle.center;
        if (this.point?.x == null || this.point?.y == null) {
            throw new Error(
                "PeekCanvasInputEditActionHandle: Point must have" +
                    " X and Y values.",
            );
        }
    }

    get center(): PointI | null {
        return this.point;
    }

    private get endLineCreateTickRadius(): number {
        return (
            this.viewArgs.config.editor.primaryEditActionHandleWidth /
            this.viewArgs.config.viewPort.zoom /
            2.0
        );
    }

    private setHandleBox() {
        const halfWidth = this.endLineCreateTickRadius;

        this.handle.box = new PeekCanvasBounds(
            this.point.x - halfWidth,
            this.point.y - halfWidth,
            2 * halfWidth,
            2 * halfWidth,
        );
    }

    wasClickedOn(point: PointI): boolean {
        this.setHandleBox();
        return this.handle.box.contains(point.x, point.y, 0);
    }

    draw(ctx: CanvasRenderingContext2D) {
        this.setHandleBox();
        switch (this.actionDisplayType) {
            case EditActionDisplayTypeE.Pencil: {
                this.drawPencil(ctx);
                break;
            }
            case EditActionDisplayTypeE.Tick: {
                this.drawTick(ctx);
                break;
            }
            default: {
                throw new Error(
                    `Unhandled ActionDisplayTypeE ${this.actionDisplayType}`,
                );
            }
        }
    }

    private get color(): string {
        switch (this.actionDisplayPriorityType) {
            case EditActionDisplayPriorityE.Success: {
                return this.viewArgs.config.editor
                    .primaryEditActionCompleteColor;
            }
            case EditActionDisplayPriorityE.Default: {
                return this.viewArgs.config.editor
                    .primaryEditActionDefaultColor;
            }
            default: {
                throw new Error(
                    `Unhandled ActionDisplayTypeE ${this.actionDisplayType}`,
                );
            }
        }
    }

    private drawTick(ctx: CanvasRenderingContext2D): void {
        const x = this.point.x;
        const y = this.point.y;
        const radius = this.endLineCreateTickRadius;
        const zoom = this.viewArgs.config.viewPort.zoom;

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath();

        ctx.beginPath();
        ctx.moveTo(x - radius / 2, y + radius / 10);
        ctx.lineTo(x - radius / 10, y + radius / 2);
        ctx.lineTo(x + radius / 2, y - radius / 2);
        ctx.lineWidth = 4 / zoom;
        ctx.strokeStyle = "white";
        ctx.stroke();
        ctx.closePath();
    }

    private drawPencil(ctx: CanvasRenderingContext2D) {
        const x = this.point.x;
        const y = this.point.y;
        const radius = this.endLineCreateTickRadius;
        const zoom = this.viewArgs.config.viewPort.zoom;

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.closePath();
        ctx.beginPath();
        ctx.rect(
            x - radius / 10,
            y - radius / 2 - radius / 10,
            radius / 5,
            (radius / 2) * 2,
        );
        ctx.rect(
            x - radius / 10,
            y - radius / 2 - radius / 10,
            radius / 5,
            radius / 10,
        );
        ctx.moveTo(x - radius / 10, y + radius / 2 - radius / 10);
        ctx.lineTo(x, y + radius / 2 + radius / 8);
        ctx.lineTo(x + radius / 10, y + radius / 2 - radius / 10);
        ctx.lineWidth = 3 / zoom;
        ctx.strokeStyle = "white";
        ctx.stroke();
        ctx.closePath();
    }
}
