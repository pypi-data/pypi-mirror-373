import {
    DispBase,
    DispBaseT,
    DispHandleI,
    DispHandleTypeE,
    DispType,
    PointI,
} from "./DispBase";
import {
    DispColor,
    DispTextStyle,
} from "@peek/peek_plugin_diagram/_private/lookups";
import {
    PeekCanvasShapePropsContext,
    ShapeProp,
    ShapePropType,
} from "../canvas/PeekCanvasShapePropsContext";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { DispPolyline, DispPolylineT } from "./DispPolyline";

export interface DispCurvedTextT extends DispBaseT {
    // Text Style
    fs: number;
    fsl: DispTextStyle;

    // Colour
    c: number;
    cl: DispColor;

    // border colour
    bc: number;
    bcl: DispColor;

    // Text
    te: string;

    // Spacing Between Text Factor
    sbt: number;
}

export class DispCurvedText extends DispBase {
    static textStyle(disp: DispCurvedTextT): DispTextStyle {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.fsl;
    }

    static setTextStyle(disp: DispCurvedTextT, val: DispTextStyle): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.fsl = val;
        disp.fs = val == null ? null : val.id;
    }

    static borderColor(disp: DispCurvedTextT): DispColor {
        return disp.bcl;
    }

    static setBorderColor(disp: DispCurvedTextT, val: DispColor): void {
        disp.bcl = val;
        disp.bc = val == null ? null : val.id;
    }

    static color(disp: DispCurvedTextT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.cl;
    }

    static setColor(disp: DispCurvedTextT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.cl = val;
        disp.c = val == null ? null : val.id;
    }

    static text(disp: DispCurvedTextT): string {
        return disp.te;
    }

    static setText(disp: DispCurvedTextT, val: string): void {
        disp.te = val;
        DispBase.setBoundsNull(disp);
    }

    static spacingBetweenTexts(disp: DispCurvedTextT): number {
        return disp.sbt || 0;
    }

    static setSpacingBetweenTexts(disp: DispCurvedTextT, val: number): void {
        disp.sbt = val;
        DispBase.setBoundsNull(disp);
    }

    static override create(coordSet: ModelCoordSet): DispCurvedTextT {
        let newDisp = {
            ...DispBase.create(coordSet, DispBase.TYPE_DCT),
            g: [], // PointsT[]
            sbt: 0, // spacing between texts
        };

        DispCurvedText.setSelectable(newDisp, true);
        DispCurvedText.setSpacingBetweenTexts(newDisp, 2);
        DispCurvedText.setText(newDisp, "New Text");

        let dispTextStyle = new DispTextStyle();
        dispTextStyle.id = coordSet.editDefaultTextStyleId;

        let dispColor = new DispColor();
        dispColor.id = coordSet.editDefaultColorId;
        let borderColor = new DispColor();
        borderColor.id = coordSet.editDefaultColorId;

        DispCurvedText.setTextStyle(newDisp, dispTextStyle);
        DispCurvedText.setColor(newDisp, dispColor);
        DispCurvedText.setBorderColor(newDisp, borderColor);

        DispCurvedText.setText(newDisp, "New Curved Text");

        return newDisp;
    }

    static contains(
        disp: DispCurvedTextT,
        point: PointI,
        margin: number,
    ): boolean {
        return DispPolyline.contains(
            disp as any as DispPolylineT,
            point,
            margin,
        );
    }

    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispBase.makeShapeContext(context);

        context.addProp(
            new ShapeProp(
                ShapePropType.MultilineString,
                DispCurvedText.text,
                DispCurvedText.setText,
                "Text",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.TextStyle,
                DispCurvedText.textStyle,
                DispCurvedText.setTextStyle,
                "Text Style",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispCurvedText.color,
                DispCurvedText.setColor,
                "Color",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispCurvedText.borderColor,
                DispCurvedText.setBorderColor,
                "Border Color",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Integer,
                DispCurvedText.spacingBetweenTexts,
                DispCurvedText.setSpacingBetweenTexts,
                "Text Spacing",
            ),
        );
    }

    // ---------------
    // Represent the disp as a user-friendly string

    static override makeShapeStr(disp: DispCurvedTextT): string {
        let center = DispCurvedText.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nText : ${DispCurvedText.text(disp)}` +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }

    // ---------------
    // Generate a list of handles to edit this shape

    static isStartHandle(disp: DispBaseT, handleIndex: number): boolean {
        if (DispBase.typeOf(disp) != DispType.curvedText) return false;

        return handleIndex == 0;
    }

    static isEndHandle(disp: DispBaseT, handleIndex: number): boolean {
        if (DispBase.typeOf(disp) != DispType.curvedText) return false;

        return handleIndex == DispCurvedText.geom(disp).length / 2 - 1;
    }

    // ---------------
    // Primary Edit Action Handle Point

    static override primaryActionHandlePoint(
        disp: DispCurvedTextT,
        margin: number,
    ): DispHandleI | null {
        if (disp.g.length < 2) {
            return null;
        }

        // For curved text, we'll position the edit handle near the first point
        // of the path, slightly offset for visibility
        return {
            disp: disp,
            center: {
                x: disp.g[0] + margin,
                y: disp.g[1] - margin,
            },
            handleType: DispHandleTypeE.primaryAction,
        };
    }

    static override handlePoints(
        disp: DispCurvedTextT,
        margin: number,
    ): DispHandleI[] {
        return DispPolyline.handlePoints(disp as any as DispPolylineT, margin);
    }
}
