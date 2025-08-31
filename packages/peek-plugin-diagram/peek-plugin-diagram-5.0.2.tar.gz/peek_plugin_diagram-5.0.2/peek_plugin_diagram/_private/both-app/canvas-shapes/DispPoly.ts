import { DispBase, DispBaseT, PointI, PointsT } from "./DispBase";
import {
    DispColor,
    DispLineStyle,
} from "@peek/peek_plugin_diagram/_private/lookups";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";

export interface DispPolyT extends DispBaseT {
    // lineColor
    lc: number;
    lcl: DispColor;

    // lineStyle
    ls: number;
    lsl: DispLineStyle;

    // lineWidth
    w: number;
}

export abstract class DispPoly extends DispBase {
    static lineColor(disp): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.lcl;
    }

    static setLineColor(disp: DispPolyT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.lcl = val;
        disp.lc = val == null ? null : val.id;
    }

    static lineStyle(disp): DispLineStyle {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.lsl;
    }

    static setLineStyle(disp: DispPolyT, val: DispLineStyle): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.lsl = val;
        disp.ls = val == null ? null : val.id;
    }

    static lineWidth(disp): number {
        return disp.w;
    }

    static setLineWidth(disp: DispPolyT, val: number): void {
        disp.w = val;
        DispBase.setBoundsNull(disp);
    }

    // ---------------
    // Support shape creating
    static override create(coordSet: ModelCoordSet, type): DispPolyT {
        let newDisp = {
            ...DispBase.create(coordSet, type),
            g: [], // PointsT[]
            w: 2,
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

    // ---------------
    // Support shape editing
    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispBase.makeShapeContext(context);

        context.addProp(
            new ShapeProp(
                ShapePropType.LineStyle,
                DispPoly.lineStyle,
                DispPoly.setLineStyle,
                "Line Style",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispPoly.lineColor,
                DispPoly.setLineColor,
                "Line Color",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispPoly.lineWidth,
                DispPoly.setLineWidth,
                "Line Width",
            ),
        );
    }
}
