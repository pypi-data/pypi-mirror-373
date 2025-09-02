import { DispPoly, DispPolyT } from "./DispPoly";
import {
    DispBase,
    DispBaseT,
    DispHandleI,
    DispHandleTypeE,
    DispType,
    PointI,
} from "./DispBase";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";
import { DispColor } from "@peek/peek_plugin_diagram/_private/lookups";
import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch/BranchTuple";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DispEdgeTemplate, DispEdgeTemplateT } from "./DispEdgeTemplate";

export interface DispPolylineT extends DispPolyT {
    // Edge Color
    ec: number;
    ecl: DispColor;

    // Border Width
    bw: number;

    // Border Color
    bc: number;
    bcl: DispColor;

    // Start Key
    sk: string;

    // End Key
    ek: string;

    // Start end type, is this an arrow, etc?
    st: number | null;

    // End End Type
    et: number | null;

    // Target Template Line ID
    ti: number;

    // Target Template Line Name
    tn: string;
}

export enum DispPolylineEndTypeE {
    None = 0,
    Arrow = 1,
    Dot = 2,
}

export class DispPolyline extends DispPoly {
    static targetGroupId(disp: DispPolylineT): number {
        return disp.ti;
    }

    static setTargetEdgeTemplateId(disp: DispPolylineT, val: number): void {
        disp.ti = val;
    }

    static setTargetEdgeTemplateName(
        disp: DispPolylineT,
        coordSetId: number,
        name: string,
    ): void {
        disp.tn = `${coordSetId}|${name}`;
    }

    static targetEdgeTemplateCoordSetId(disp: DispPolylineT): number | null {
        if (disp.tn == null || disp.tn.indexOf("|") === -1) return null;
        return parseInt(disp.tn.split("|")[0]);
    }

    static targetEdgeTemplateName(disp: DispPolylineT): string | null {
        if (disp.tn == null || disp.tn.indexOf("|") === -1) return null;
        return disp.tn.split("|")[1];
    }

    /** Edge Color
     *
     * And alternate color of this polyline, used to color it if it's representing an
     * edge of a GraphDB.
     */
    static edgeColor(disp: DispPolylineT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.ecl;
    }

    /** Set Edge Color
     *
     */
    static setEdgeColor(disp: DispPolylineT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.ecl = val;
        disp.ec = val == null ? null : val.id;
    }

    /** Border Width
     *
     * The width of the border underneath the polyline
     */
    static borderWidth(disp: DispPolylineT): number | null {
        return disp.bw;
    }

    /** Set Border Width
     *
     */
    static setBorderWidth(disp: DispPolylineT, val: number | null): void {
        disp.bw = val;
    }

    /** Border Color
     *
     * The color of the border underneath the polyline
     */
    static borderColor(disp: DispPolylineT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.bcl;
    }

    /** Set Border Color
     *
     */
    static setBorderColor(disp: DispPolylineT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.bcl = val;
        disp.bc = val == null ? null : val.id;
    }

    /** Start Key
     *
     * The key of another disp object if the start of this polyline is related to it
     */
    static startKey(disp: DispPolylineT): string | null {
        return disp.sk;
    }

    /** End Key
     *
     * The key of another disp object if the end of this polyline is related to it
     */
    static endKey(disp: DispPolylineT): string | null {
        return disp.ek;
    }

    /** Start Key
     *
     * The key of another disp object if the start of this polyline is related to it
     */
    static startEndType(disp: DispPolylineT): DispPolylineEndTypeE {
        return disp.st || 0;
    }

    static setStartEndType(disp: DispPolylineT, val: number | null): void {
        disp.st = val == 0 ? null : val;
    }

    /** End Key
     *
     * The key of another disp object if the end of this polyline is related to it
     */
    static endEndType(disp: DispPolylineT): DispPolylineEndTypeE {
        return disp.et || 0;
    }

    static setEndEndType(disp: DispPolylineT, val: number | null): void {
        disp.et = val == 0 ? null : val;
    }

    /** Start End Keys
     *
     * This method returns a unique list af the start and end keys of the selected
     * polylines.
     *
     * Non-polylines are ignored.
     *
     * @param disps: A list of shapes
     * @return: A list of start and end keys
     */
    static startEndKeys(disps: any[]): string[] {
        let keysDict = {};
        for (let disp of disps) {
            if (DispBase.typeOf(disp) != DispType.polyline) continue;

            let startKey = DispPolyline.startKey(disp);
            let endKey = DispPolyline.endKey(disp);

            if (startKey != null) keysDict[startKey] = true;
            else if (endKey != null) keysDict[endKey] = true;
        }
        return Object.keys(keysDict);
    }

    static override create(coordSet: ModelCoordSet): DispPolylineT {
        return <DispPolylineT>DispPoly.create(coordSet, DispBase.TYPE_DPL);
    }

    static contains(
        dispPoly: DispPolylineT,
        point: PointI,
        margin: number,
    ): boolean {
        const x = point.x;
        const y = point.y;

        const points = DispPolyline.geom(dispPoly);
        let x1 = points[0];
        let y1 = points[1];
        for (let i = 2; i < points.length; i += 2) {
            let x2 = points[i];
            let y2 = points[i + 1];

            let dx = x2 - x1;
            let dy = y2 - y1;

            // For Bounding Box
            let left = (x1 < x2 ? x1 : x2) - margin;
            let right = (x1 < x2 ? x2 : x1) + margin;
            let top = (y1 < y2 ? y1 : y2) - margin;
            let bottom = (y1 < y2 ? y2 : y1) + margin;

            // Special condition for vertical lines
            if (dx == 0) {
                if (left <= x && x <= right && top <= y && y <= bottom) {
                    return true;
                }
            }

            let slope = dy / dx;
            // y = mx + c
            // intercept c = y - mx
            let intercept = y1 - slope * x1; // which is same as y2 - slope * x2

            let yVal = slope * x + intercept;
            let xVal = (y - intercept) / slope;

            if (
                ((y - margin < yVal && yVal < y + margin) ||
                    (x - margin < xVal && xVal < x + margin)) &&
                left <= x &&
                x <= right &&
                top <= y &&
                y <= bottom
            )
                return true;

            x1 = x2;
            y1 = y2;
        }

        return false;
    }

    // ---------------
    // Support shape editing
    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispPoly.makeShapeContext(context);

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispPolyline.borderWidth,
                DispPolyline.setBorderWidth,
                "Border Width",
                { allowNullOption: true },
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispPolyline.borderColor,
                DispPolyline.setBorderColor,
                "Border Color",
                { allowNullOption: true },
            ),
        );

        let lineEndOptions = [
            {
                name: "None",
                object: { id: DispPolylineEndTypeE.None },
                value: DispPolylineEndTypeE.None,
            },
            {
                name: "Arrow",
                object: { id: DispPolylineEndTypeE.Arrow },
                value: DispPolylineEndTypeE.Arrow,
            },
            {
                name: "Dot",
                object: { id: DispPolylineEndTypeE.Dot },
                value: DispPolylineEndTypeE.Dot,
            },
        ];

        context.addProp(
            new ShapeProp(
                ShapePropType.Option,
                (disp) => {
                    // The UI expects an object with an ID
                    return { id: DispPolyline.startEndType(disp) };
                },
                (disp, valObj) => DispPolyline.setStartEndType(disp, valObj.id),
                "Line Start Style",
                { options: lineEndOptions },
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Option,
                (disp) => {
                    // The UI expects an object with an ID
                    return { id: DispPolyline.endEndType(disp) };
                },
                (disp, valObj) => DispPolyline.setEndEndType(disp, valObj.id),
                "Line End Style",
                { options: lineEndOptions },
            ),
        );
    }

    /** Set Target Line
     *
     * Change the template that this polyline immitates
     *
     *
     * @param polyline
     * @param edgeTemplate
     * @param edgeTemplateCoordSetId
     * @param lookupService
     * @param branchTuple
     */
    static setEdgeTemplate(
        polyline: DispPolylineT,
        edgeTemplate: DispEdgeTemplateT,
        edgeTemplateCoordSetId: number,
        lookupService: PrivateDiagramLookupService,
        branchTuple: BranchTuple,
    ): void {
        const templateName = DispEdgeTemplate.templateName(edgeTemplate);
        // Levels need to be converted to the correct coordSetId
        const levels = lookupService.levelsOrderedByOrder(
            branchTuple.coordSetId,
        );
        const templateLevel = DispEdgeTemplate.level(edgeTemplate);
        const levelForCoordSet = levels.find(
            (level) => level.importHash === templateLevel.importHash,
        );

        if (levelForCoordSet == null) {
            throw new Error(
                `Could not equivalent level` +
                    ` for '${templateLevel.name}' (${templateLevel.id})` +
                    ` when applying template '${templateName}'`,
            );
        }

        DispPolyline.setTargetEdgeTemplateName(
            polyline,
            edgeTemplateCoordSetId,
            templateName,
        );

        DispPolyline.setLayer(polyline, DispEdgeTemplate.layer(edgeTemplate));
        DispPolyline.setLevel(polyline, levelForCoordSet);

        DispPolyline.setLineWidth(
            polyline,
            DispEdgeTemplate.lineWidth(edgeTemplate),
        );
        DispPolyline.setLineColor(
            polyline,
            DispEdgeTemplate.lineColor(edgeTemplate),
        );
        DispPolyline.setLineStyle(
            polyline,
            DispEdgeTemplate.lineStyle(edgeTemplate),
        );

        DispPolyline.setEndEndType(
            polyline,
            DispEdgeTemplate.endEndType(edgeTemplate),
        );
        DispPolyline.setStartEndType(
            polyline,
            DispEdgeTemplate.startEndType(edgeTemplate),
        );
    }

    // ---------------
    // Represent the disp as a user friendly string

    static override makeShapeStr(disp: DispBaseT): string {
        let center = DispPolyline.center(disp as DispPolylineT);
        return (
            DispBase.makeShapeStr(disp) +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }

    // ---------------
    // Generate a list of handles to edit this shape

    static isStartHandle(disp: DispBaseT, handleIndex: number): boolean {
        if (DispBase.typeOf(disp) != DispType.polyline) return false;

        return handleIndex == 0;
    }

    static isEndHandle(disp: DispBaseT, handleIndex: number): boolean {
        if (DispBase.typeOf(disp) != DispType.polyline) return false;

        return handleIndex == DispPolyline.geom(disp).length / 2 - 1;
    }

    // ---------------
    // Primary Edit Action Handle Point

    static override primaryActionHandlePoint(
        disp: DispPolylineT,
        margin: number,
    ): DispHandleI | null {
        return null;
    }

    static override handlePoints(
        disp: DispPolylineT,
        margin: number,
    ): DispHandleI[] {
        const result: DispHandleI[] = [];

        let points = DispPolyline.geom(disp);

        function addHandle(p: PointI, ref: PointI) {
            let adj = p.x - ref.x;
            let opp = p.y - ref.y;
            let hypot = Math.sqrt(Math.pow(adj, 2) + Math.pow(opp, 2));

            let multiplier = margin / hypot;

            result.push({
                disp: disp,
                center: {
                    x: p.x + adj * multiplier,
                    y: p.y + opp * multiplier,
                },
                handleType: DispHandleTypeE.movePoint,
            });
        }

        function pointForIndex(index: number) {
            index *= 2;
            return { x: points[index], y: points[index + 1] };
        }

        let firstXy = { x: points[0], y: points[1] };
        addHandle(pointForIndex(0), pointForIndex(1));

        let lastXy = firstXy;
        for (let i = 1; i < points.length / 2; ++i) {
            let thisXy = pointForIndex(i);
            let refXy = lastXy;

            // If this is not the last point
            if (i + 2 <= points.length / 2) {
                let nextXy = pointForIndex(i + 1);

                refXy = {
                    x: (lastXy.x + nextXy.x) / 2,
                    y: (lastXy.y + nextXy.y) / 2,
                };
            }
            addHandle(thisXy, refXy);
            lastXy = thisXy;
        }

        return result;
    }
}
