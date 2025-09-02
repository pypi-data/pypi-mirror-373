import {
    DispBase,
    DispBaseT,
    DispHandleI,
    DispHandleTypeE,
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

export enum TextVerticalAlign {
    top = -1,
    center = 0,
    bottom = 1,
}

export enum TextHorizontalAlign {
    left = -1,
    center = 0,
    right = 1,
}

export interface DispTextT extends DispBaseT {
    // Text Style
    fs: number;
    fsl: DispTextStyle;

    // Colour
    c: number;
    cl: DispColor;

    // border colour
    bc: number;
    bcl: DispColor;

    // Vertical Alignment
    va: number;

    // Horizontal Alignment
    ha: number;

    // Rotation
    r: number;

    // Text
    te: string;

    // Text Height (Optional)
    th: number | null;

    // Horizontal Stretch (default 1)
    hs: number;
}

export class DispText extends DispBase {
    static textStyle(disp: DispTextT): DispTextStyle {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.fsl;
    }

    static setTextStyle(disp: DispTextT, val: DispTextStyle): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.fsl = val;
        disp.fs = val == null ? null : val.id;
    }

    static borderColor(disp: DispTextT): DispColor {
        return disp.bcl;
    }

    static setBorderColor(disp: DispTextT, val: DispColor): void {
        disp.bcl = val;
        disp.bc = val == null ? null : val.id;
    }

    static color(disp: DispTextT): DispColor {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.cl;
    }

    static setColor(disp: DispTextT, val: DispColor): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.cl = val;
        disp.c = val == null ? null : val.id;
    }

    static verticalAlign(disp: DispTextT): TextVerticalAlign {
        let val = disp.va;
        if (val == TextVerticalAlign.top) return TextVerticalAlign.top;
        if (val == TextVerticalAlign.bottom) return TextVerticalAlign.bottom;
        return TextVerticalAlign.center;
    }

    static setVerticalAlign(disp: DispTextT, value: number): void {
        disp.va = value;
    }

    static horizontalAlign(disp: DispTextT): TextHorizontalAlign {
        let val = disp.ha;
        if (val == TextHorizontalAlign.left) return TextHorizontalAlign.left;
        if (val == TextHorizontalAlign.right) return TextHorizontalAlign.right;
        return TextHorizontalAlign.center;
    }

    static setHorizontalAlign(disp: DispTextT, value: number): void {
        disp.ha = value;
    }

    static rotation(disp: DispTextT): number {
        return disp.r;
    }

    static text(disp: DispTextT): string {
        return disp.te;
    }

    static setText(disp: DispTextT, val: string): void {
        disp.te = val;
        DispBase.setBoundsNull(disp);
    }

    static height(disp: DispTextT): number | null {
        return disp.th;
    }

    static horizontalStretch(disp: DispTextT): number {
        return disp.hs;
    }

    static centerPointX(disp: DispTextT): number {
        return disp.g[0];
    }

    static centerPointY(disp: DispTextT): number {
        return disp.g[1];
    }

    static setCenterPoint(disp: DispTextT, x: number, y: number): void {
        disp.g = [x, y];
        DispBase.setBoundsNull(disp);
    }

    static override create(coordSet: ModelCoordSet): DispTextT {
        let newDisp = {
            ...DispBase.create(coordSet, DispBase.TYPE_DT),
            // From Text
            va: TextVerticalAlign.center, // TextVerticalAlign.center
            ha: TextHorizontalAlign.center, // TextHorizontalAlign.center
            r: 0, // number
            th: null, // number | null
            hs: 1, // number | null
        };

        DispText.setSelectable(newDisp, true);
        DispText.setText(newDisp, "New Text");

        let dispTextStyle = new DispTextStyle();
        dispTextStyle.id = coordSet.editDefaultTextStyleId;

        let dispColor = new DispColor();
        dispColor.id = coordSet.editDefaultColorId;

        DispText.setTextStyle(newDisp, dispTextStyle);
        DispText.setColor(newDisp, dispColor);

        DispText.setText(newDisp, "New Text");
        DispText.setCenterPoint(newDisp, 0, 0);

        return newDisp;
    }

    static override makeShapeContext(
        context: PeekCanvasShapePropsContext,
    ): void {
        DispBase.makeShapeContext(context);

        context.addProp(
            new ShapeProp(
                ShapePropType.MultilineString,
                DispText.text,
                DispText.setText,
                "Text",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.TextStyle,
                DispText.textStyle,
                DispText.setTextStyle,
                "Text Style",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispText.color,
                DispText.setColor,
                "Color",
            ),
        );

        context.addProp(
            new ShapeProp(
                ShapePropType.Color,
                DispText.borderColor,
                DispText.setBorderColor,
                "Border Color",
            ),
        );

        const textVerticleAlignOptions = [
            {
                name: "Top",
                object: { id: TextVerticalAlign.top },
                value: TextVerticalAlign.top,
            },
            {
                name: "Center",
                object: { id: TextVerticalAlign.center },
                value: TextVerticalAlign.center,
            },
            {
                name: "Bottom",
                object: { id: TextVerticalAlign.bottom },
                value: TextVerticalAlign.bottom,
            },
        ];

        context.addProp(
            new ShapeProp(
                ShapePropType.Option,
                (disp) => {
                    // The UI expects an object with an ID
                    return { id: DispText.verticalAlign(disp) };
                },
                (disp, valObj) => DispText.setVerticalAlign(disp, valObj.id),
                "Vertical Align",
                { options: textVerticleAlignOptions },
            ),
        );

        const textHorizontalAlignOptions = [
            {
                name: "Left",
                object: { id: TextHorizontalAlign.left },
                value: TextHorizontalAlign.left,
            },
            {
                name: "Center",
                object: { id: TextHorizontalAlign.center },
                value: TextHorizontalAlign.center,
            },
            {
                name: "Right",
                object: { id: TextHorizontalAlign.right },
                value: TextHorizontalAlign.right,
            },
        ];

        context.addProp(
            new ShapeProp(
                ShapePropType.Option,
                (disp) => {
                    // The UI expects an object with an ID
                    return { id: DispText.horizontalAlign(disp) };
                },
                (disp, valObj) => DispText.setHorizontalAlign(disp, valObj.id),
                "Horizontal Align",
                { options: textHorizontalAlignOptions },
            ),
        );
    }

    // ---------------
    // Represent the disp as a user friendly string

    static override makeShapeStr(disp: DispTextT): string {
        let center = DispText.center(disp);
        return (
            DispBase.makeShapeStr(disp) +
            `\nText : ${DispText.text(disp)}` +
            `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`
        );
    }

    // ---------------
    // Primary Edit Action Handle Point

    static override primaryActionHandlePoint(
        disp: DispTextT,
        margin: number,
    ): DispHandleI | null {
        if (disp.bounds == null) {
            return null;
        }

        const center = DispText.center(disp);

        let offset = 0;
        const align = DispText.horizontalAlign(disp);
        switch (align) {
            case TextHorizontalAlign.left:
                offset = disp.bounds.width;
                break;

            case TextHorizontalAlign.center:
                offset = disp.bounds.width / 2;
                break;

            case TextHorizontalAlign.right:
                offset = 0;
                break;
            default:
                throw new Error(
                    `DispText.primaryActionHandlePoint unhandled` +
                        ` allign ${align}`,
                );
        }

        return {
            disp: disp,
            center: {
                x: center.x + disp.bounds.width - offset + margin,
                y: center.y,
            },
            handleType: DispHandleTypeE.primaryAction,
        };
    }
}
