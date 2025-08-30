import { DispPoly, DispPolyT } from "./DispPoly";
import { DispBase } from "./DispBase";
import { DispPolylineEndTypeE } from "./DispPolyline";

export interface DispEdgeTemplateT extends DispPolyT {
    // Name
    n: string;

    // Start end type, is this an arrow, etc?
    st: number | null;

    // End End Type
    et: number | null;
}

export class DispEdgeTemplate extends DispPoly {
    /** Name
     *
     * The name of this line template
     */
    static templateName(disp: DispEdgeTemplateT): string {
        return disp.n;
    }

    /** Start Key
     *
     * The key of another disp object if the start of this EdgeTemplate is related to it
     */
    static startEndType(disp: DispEdgeTemplateT): DispPolylineEndTypeE {
        return disp.st || 0;
    }

    static setStartEndType(disp: DispEdgeTemplateT, val: number | null): void {
        disp.st = val == 0 ? null : val;
    }

    /** End Key
     *
     * The key of another disp object if the end of this EdgeTemplate is related to it
     */
    static endEndType(disp: DispEdgeTemplateT): DispPolylineEndTypeE {
        return disp.et || 0;
    }

    static setEndEndType(disp: DispEdgeTemplateT, val: number | null): void {
        disp.et = val == 0 ? null : val;
    }

    // ---------------
    // Represent the disp as a user friendly string

    static override makeShapeStr(disp: DispEdgeTemplateT): string {
        return DispBase.makeShapeStr(disp) + `\nName : ${disp.n}`;
    }
}
