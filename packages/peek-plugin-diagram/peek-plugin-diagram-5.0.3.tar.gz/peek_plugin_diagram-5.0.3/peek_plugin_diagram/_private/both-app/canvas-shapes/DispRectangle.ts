import { DispBase, PointI } from "./DispBase";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";
import { DispPolygon, DispPolygonT } from "./DispPolygon";
import { assert } from "../DiagramUtil";

/** Disp Rectangle
 *
 * This is a polyline with four points and a flag set.
 *
 * Geom = [
 *  x, y,                   // [0], [1], Lower Left
 *  x + width, y,           // [2], [3], Lower Right
 *  x + width, y + height   // [4], [5], Upper Right
 *  x, y + height           // [6], [7], Upper Left
 *
 */
export class DispRectangle extends DispPolygon {
    static setRectanglePoint(disp: DispPolygonT, point: PointI): void {
        if (disp.g.length != 8)
            throw new Error("Polygon rectangle doesn't have four points");
        disp.g[0] = point.x;
        disp.g[1] = point.y;
        disp.g[3] = point.y;
        disp.g[6] = point.x;
        DispBase.setBoundsNull(disp);
    }

    static setRectangleWidth(disp: DispPolygonT, width: number): void {
        if (disp.g.length != 8)
            throw new Error("Polygon rectangle doesn't have four points");
        let x = disp.g[0];
        disp.g[2] = x + width;
        disp.g[4] = x + width;
        DispBase.setBoundsNull(disp);
    }

    static setRectangleHeight(disp: DispPolygonT, height: number): void {
        if (disp.g.length != 8)
            throw new Error("Polygon rectangle doesn't have four points");
        let y = disp.g[1];
        disp.g[5] = y + height;
        disp.g[7] = y + height;
        DispBase.setBoundsNull(disp);
    }

    static override center(disp: DispPolygonT): PointI {
        return { x: disp.g[0], y: disp.g[1] };
    }

    static override create(coordSet: ModelCoordSet): DispPolygonT {
        let disp = <DispPolygonT>DispPolygon.create(coordSet);
        DispPolygon.setIsRectangle(disp, true);
        disp.g = [0, 0, 0, 0, 0, 0, 0, 0];
        return disp;
    }
}
