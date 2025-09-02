import { DispColor } from "@peek/peek_plugin_diagram/_private/lookups";
import { DispPoly, DispPolyT } from "./DispPoly";
import { DispBase, PointI } from "./DispBase";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";
import { PeekCanvasBounds } from "../canvas/PeekCanvasBounds";

export enum PolygonFillDirection {
    fillTopToBottom = 0,
    fillBottomToTop = 1,
    fillRightToLeft = 2,
    fillLeftToRight = 3,
}

export interface DispPolygonT extends DispPolyT {
    // fillColor
    fc: number;
    fcl: DispColor;

    // cornerRadius
    cr: number;

    // fillDirection
    fd: number;

    // fillPercent
    fp: number;

    // Is this polygon a rectangle
    r: boolean | null;
}

export class DispPolygon extends DispPoly {
    static fillColor(disp: DispPolygonT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.fcl;
    }

    static setFillColor(disp: DispPolygonT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.fcl = val;
        disp.fc = val == null ? null : val.id;
    }

    static cornerRadius(disp: DispPolygonT): number {
        return disp.cr;
    }

    static setCornerRadius(disp: DispPolygonT, val: number): void {
        disp.cr = val;
    }

    static fillDirection(disp: DispPolygonT): PolygonFillDirection {
        let val = disp.fd;
        if (val == PolygonFillDirection.fillBottomToTop)
            return PolygonFillDirection.fillBottomToTop;

        if (val == PolygonFillDirection.fillRightToLeft)
            return PolygonFillDirection.fillRightToLeft;

        if (val == PolygonFillDirection.fillLeftToRight)
            return PolygonFillDirection.fillLeftToRight;

        // Else, default to Top to Bottom
        return PolygonFillDirection.fillTopToBottom;
    }

    static setFillDirection(disp: DispPolygonT, val: number): void {
        disp.fd = val;
    }

    static fillPercent(disp: DispPolygonT): number | null {
        const fillPercentage = disp.fp;
        if (fillPercentage == null) return null;

        return Math.max(0.0, Math.min(100.0, fillPercentage));
    }

    static setFillPercent(disp: DispPolygonT, val: number): void {
        disp.fp = val;
    }

    static isRectangle(disp: DispPolygonT): boolean {
        return !!disp.r;
    }

    static setIsRectangle(disp: DispPolygonT, val: boolean): void {
        disp.r = !val ? null : true;
    }

    static contains(
        disp: DispPolygonT,
        point: PointI,
        margin: number,
    ): boolean {
        const x = point.x;
        const y = point.y;

        const points = DispPolygon.geom(disp);

        // Using the polygon line segment crossing algorithm.
        function rayCrossesSegment(
            x: number,
            y: number,
            axIn: number,
            ayIn: number,
            bxIn: number,
            byIn: number,
        ) {
            let swap = ayIn > byIn;
            let ax = swap ? bxIn : axIn;
            let ay = swap ? byIn : ayIn;
            let bx = swap ? axIn : bxIn;
            let by = swap ? ayIn : byIn;

            // alter longitude to cater for 180 degree crossings
            // JJC, I don't think we need this, we're not using spatial references
            /*
             if (x < 0)
             x += 360;
             if (ax < 0)
             ax += 360;
             if (bx < 0)
             bx += 360;
             */

            if (y == ay || y == by) y += 0.00000001;
            if (y > by || y < ay || x > Math.max(ax, bx)) return false;
            if (x < Math.min(ax, bx)) return true;

            let red = ax != bx ? (by - ay) / (bx - ax) : Infinity;
            let blue = ax != x ? (y - ay) / (x - ax) : Infinity;
            return blue >= red;
        }

        let crossings = 0;

        let pFirstX = points[0];
        let pFirstY = points[1];
        let p1x = pFirstX;
        let p1y = pFirstY;

        // This will deliberately run one more iteration after the last pointY
        for (let i = 2; i <= points.length; i += 2) {
            // Assume this is the last iteration by default
            let p2x = pFirstX;
            let p2y = pFirstY;

            // If not, set it to the proper point.
            if (i != points.length) {
                p2x = points[i];
                p2y = points[i + 1];
            }

            if (rayCrossesSegment(x, y, p1x, p1y, p2x, p2y)) crossings++;

            p1x = p2x;
            p1y = p2y;
        }

        // odd number of crossings?
        return crossings % 2 == 1;
    }

    static override create(coordSet: ModelCoordSet): DispPolygonT {
        let disp = <DispPolygonT>DispPoly.create(coordSet, DispBase.TYPE_DPG);
        DispPolygon.setCornerRadius(disp, 0);
        DispPolygon.setFillDirection(
            disp,
            PolygonFillDirection.fillTopToBottom,
        );
        DispPolygon.setFillPercent(disp, 100);
        return disp;
    }

    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispPoly.makeShapeContext(context);

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispPolygon.fillColor,
                DispPolygon.setFillColor,
                "Fill Color",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Option,
                (disp) => {
                    // The UI expects an object with an ID
                    return { id: DispPolygon.fillDirection(disp) };
                },
                (disp, valObj) => DispPolygon.setFillDirection(disp, valObj.id),
                "Fill Direction",
                {
                    options: [
                        {
                            name: "Bottom to Top",
                            object: {
                                id: PolygonFillDirection.fillBottomToTop,
                            },
                            value: PolygonFillDirection.fillBottomToTop,
                        },
                        {
                            name: "Right to Left",
                            object: {
                                id: PolygonFillDirection.fillRightToLeft,
                            },
                            value: PolygonFillDirection.fillRightToLeft,
                        },
                        {
                            name: "Left to Right",
                            object: {
                                id: PolygonFillDirection.fillLeftToRight,
                            },
                            value: PolygonFillDirection.fillLeftToRight,
                        },
                        {
                            name: "Top to Bottom",
                            object: {
                                id: PolygonFillDirection.fillTopToBottom,
                            },
                            value: PolygonFillDirection.fillTopToBottom,
                        },
                    ],
                },
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispPolygon.fillPercent,
                DispPolygon.setFillPercent,
                "Fill Percent",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispPolygon.cornerRadius,
                DispPolygon.setCornerRadius,
                "Corner Radius",
            ),
        );
    }

    // ---------------
    // Represent the disp as a user friendly string

    static override makeShapeStr(disp: DispPolygonT): string {
        let center = DispPolygon.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }
}
