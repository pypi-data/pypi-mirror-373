import { DispGroupPointerT } from "./DispGroupPointer";

export abstract class DispGroupPointerPartial {
    static targetGroupId(disp: DispGroupPointerT): number {
        return disp.tg;
    }

    static setTargetGroupId(disp: DispGroupPointerT, val: number): void {
        disp.tg = val;
    }

    static setTargetGroupName(
        disp: DispGroupPointerT,
        coordSetId: number,
        name: string
    ): void {
        disp.tn = `${coordSetId}|${name}`;
    }
}
