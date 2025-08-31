import { DispBase, DispBaseT, PointI } from "./DispBase";
import {
    DispColor,
    DispLineStyle,
} from "@peek/peek_plugin_diagram/_private/lookups";
import { DispPoly } from "./DispPoly";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";

export interface DispEllipseT extends DispBaseT {
    // fillColor
    fc: number;
    fcl: DispColor;

    // lineColor
    lc: number;
    lcl: DispColor;

    // lineStyle
    ls: number;
    lsl: DispLineStyle;

    // lineWidth
    w: number;

    // xRadius
    xr: number;

    // yRadius
    yr: number;

    // rotation
    r: number;

    // startAngle
    sa: number;

    // endAngle
    ea: number;
}

export class DispEllipse extends DispBase {
    static fillColor(disp: DispEllipseT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.fcl;
    }

    static setFillColor(disp: DispEllipseT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.fcl = val;
        disp.fc = val == null ? null : val.id;
    }

    static lineColor(disp: DispEllipseT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.lcl;
    }

    static setLineColor(disp: DispEllipseT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.lcl = val;
        disp.lc = val == null ? null : val.id;
    }

    static lineStyle(disp: DispEllipseT): DispLineStyle {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.lsl;
    }

    static setLineStyle(disp: DispEllipseT, val: DispLineStyle): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.lsl = val;
        disp.ls = val == null ? null : val.id;
    }

    static lineWidth(disp: DispEllipseT): number {
        return disp.w;
    }

    static setLineWidth(disp: DispEllipseT, val: number): void {
        disp.w = val;
    }

    static centerPointX(disp: DispEllipseT): number {
        return disp.g[0];
    }

    static centerPointY(disp: DispEllipseT): number {
        return disp.g[1];
    }

    static setCenter(disp: DispEllipseT, val: PointI): void {
        disp.g[0] = val.x;
        disp.g[1] = val.y;
        DispBase.setBoundsNull(disp);
    }

    static xRadius(disp: DispEllipseT): number {
        return disp.xr;
    }

    static setXRadius(disp: DispEllipseT, val: number): void {
        disp.xr = val;
        DispBase.setBoundsNull(disp);
    }

    static yRadius(disp: DispEllipseT): number {
        return disp.yr;
    }

    static setYRadius(disp: DispEllipseT, val: number): void {
        disp.yr = val;
        DispBase.setBoundsNull(disp);
    }

    static rotation(disp: DispEllipseT): number {
        return disp.r;
    }

    static setRotation(disp: DispEllipseT, val: number): void {
        disp.r = val;
        DispBase.setBoundsNull(disp);
    }

    static startAngle(disp: DispEllipseT): number {
        return disp.sa;
    }

    static setStartAngle(disp: DispEllipseT, val: number): void {
        disp.sa = val;
        DispBase.setBoundsNull(disp);
    }

    static endAngle(disp: DispEllipseT): number {
        return disp.ea;
    }

    static setEndAngle(disp: DispEllipseT, val: number): void {
        disp.ea = val;
        DispBase.setBoundsNull(disp);
    }

    static override rotateAboutAxis(
        disp,
        center: PointI,
        rotationDegrees: number,
    ) {
        if (disp.g == null) return;

        DispBase.rotateAboutAxis(disp, center, rotationDegrees);
        DispEllipse.setRotation(
            disp,
            DispEllipse.rotation(disp) + rotationDegrees,
        );
    }

    // ---------------
    // Create Method

    static override create(coordSet: ModelCoordSet): DispEllipseT {
        let newDisp = {
            ...DispBase.create(coordSet, DispBase.TYPE_DE),
            g: [], // PointsT[]
            w: 2, // lineWidth
            r: 0, // rotation
            sa: 0, // startAngle
            ea: 360, // endAngle
        };

        DispBase.setSelectable(newDisp, true);

        let dispLineStype = new DispLineStyle();
        dispLineStype.id = coordSet.editDefaultLineStyleId;

        let dispColor = new DispColor();
        dispColor.id = coordSet.editDefaultColorId;

        DispPoly.setLineStyle(newDisp, dispLineStype);
        DispPoly.setLineColor(newDisp, dispColor);

        return newDisp;
    }

    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispBase.makeShapeContext(context);

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispEllipse.fillColor,
                DispEllipse.setFillColor,
                "Fill Color",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.LineStyle,
                DispEllipse.lineStyle,
                DispEllipse.setLineStyle,
                "Line Style",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispEllipse.lineColor,
                DispEllipse.setLineColor,
                "Line Color",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispEllipse.lineWidth,
                DispEllipse.setLineWidth,
                "Line Width",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispEllipse.rotation,
                DispEllipse.setRotation,
                "Rotation",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispEllipse.startAngle,
                DispEllipse.setStartAngle,
                "Start Angle",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispEllipse.endAngle,
                DispEllipse.setEndAngle,
                "End Angle",
            ),
        );
    }

    // ---------------
    // Represent the disp as a user friendly string

    static override makeShapeStr(disp: DispEllipseT): string {
        let center = DispEllipse.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }
}
