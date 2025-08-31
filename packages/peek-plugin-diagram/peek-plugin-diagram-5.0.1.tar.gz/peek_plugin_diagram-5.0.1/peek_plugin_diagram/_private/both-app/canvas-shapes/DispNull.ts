import { DispBase, DispBaseT, PointI, PointsT } from "./DispBase";
import { PeekCanvasShapePropsContext } from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";
import { DispNullPartial, DispNullT } from "./DispNullPartial";

export { DispNullT } from "./DispNullPartial";

export class DispNull extends DispBase {
    static override geom(disp: DispNullT): PointsT {
        return disp.g;
    }

    static centerPointX(disp: DispNullT): number {
        return disp.g[0];
    }

    static centerPointY(disp: DispNullT): number {
        return disp.g[1];
    }

    static setGeomFromBounds(disp: DispNullT, bounds: PeekCanvasBounds): void {
        DispNullPartial.setGeomFromBounds(disp, bounds);
    }

    static override create(coordSet: ModelCoordSet): DispNullT {
        return <DispNullT>DispBase.create(coordSet, DispBase.TYPE_DN);
    }

    static createFromShape(disp: DispBaseT, replacesHashId: string): DispNullT {
        if (disp.bounds == null)
            throw new Error("Can not delete a disp with no bounds");

        const nullDisp = <DispNullT>{
            // Type
            _tt: DispBase.TYPE_DN,

            // Level
            le: disp.le,
            lel: disp.lel,

            // Layer
            la: disp.la,
            lal: disp.lal,
        };
        DispBase.setReplacesHashId(nullDisp, replacesHashId);

        // This works if there is a bounds
        if (disp.bounds.width || disp.bounds.height) {
            DispNull.setGeomFromBounds(nullDisp, disp.bounds);
        } else {
            // Make sure updateBounds is called for each shape before replacing them"
            // Otherwise they will be filtered out of the grids by the
            // DispCompiler
            console.log(
                "ERROR: Failed to create DispNull geom," +
                    " DEVELOPER: Make sure updateBounds is called for each shape before" +
                    " replacing them",
            );
        }

        return nullDisp;
    }

    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispBase.makeShapeContext(context);
    }

    // ---------------
    // Represent the disp as a user friendly string

    static override makeShapeStr(disp: DispNullT): string {
        let center = DispNull.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }
}
