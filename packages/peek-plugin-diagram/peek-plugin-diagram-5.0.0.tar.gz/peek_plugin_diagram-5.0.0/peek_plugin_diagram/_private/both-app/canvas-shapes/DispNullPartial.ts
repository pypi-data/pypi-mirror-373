import { DispBaseT } from "./DispBase";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";

export interface DispNullT extends DispBaseT {}

export class DispNullPartial {
    static setGeomFromBounds(disp: DispNullT, bounds: PeekCanvasBounds): void {
        disp.g = [
            bounds.x,
            bounds.y, // Bottom Left
            bounds.x + bounds.w,
            bounds.y, // Bottom Right
            bounds.x + bounds.w,
            bounds.y + bounds.h, // Top Right
            bounds.x,
            bounds.y + bounds.h, // Top Left
        ];
    }
}
