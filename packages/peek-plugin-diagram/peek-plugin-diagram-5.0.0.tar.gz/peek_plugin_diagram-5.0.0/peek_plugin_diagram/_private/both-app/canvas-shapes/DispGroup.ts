import { DispBase, DispBaseT } from "./DispBase";

export interface DispGroupT extends DispBaseT {
    // Disp Items
    di: string;

    // Name
    n: string;
}

export class DispGroup extends DispBase {
    static items(disp: DispGroupT): DispBaseT[] {
        if (disp.di == null) return [];

        return JSON.parse(disp.di);
    }

    static groupName(disp: DispGroupT): string {
        return disp.n;
    }

    /*
     static create(coordSet: ModelCoordSet): DispGroupPointerT {
     let newDisp = {
     ...DispBase.create(DispBase.TYPE_DGP, coordSet),
     // From Text
     'tg': null, // TextVerticalAlign.targetGroupId
     'vs': 1.0, // TextHorizontalAlign.verticalScale
     'hs': 1.0,  // TextHorizontalAlign.horizontalScale
     };
     
     DispGroupPointer.setSelectable(newDisp, true);
     DispGroupPointer.setCenterPoint(newDisp, 0, 0);
     
     return newDisp;
     }
     
     static makeShapeContext(context: PeekCanvasShapePropsContext): void {
     DispBase.makeShapeContext(context);
     
     // context.addProp(new ShapeProp(
     //     ShapePropType.MultilineString,
     //     DispGroupPointer.text,
     //     DispGroupPointer.setText,
     //     "Text"
     // ));
     //
     // context.addProp(new ShapeProp(
     //     ShapePropType.TextStyle,
     //     DispGroupPointer.textStyle,
     //     DispGroupPointer.setTextStyle,
     //     "Text Style"
     // ));
     //
     // context.addProp(new ShapeProp(
     //     ShapePropType.Color,
     //     DispGroupPointer.color,
     //     DispGroupPointer.setColor,
     //     "Color"
     // ));
     }
     
     // ---------------
     // Represent the disp as a user friendly string
     
     static makeShapeStr(disp: DispGroupPointerT): string {
     let center = DispGroupPointer.center(disp);
     return DispBase.makeShapeStr(disp)
     + `\nText : ${DispGroupPointer.targetGroupId(disp)}`
     + `\nAt : ${parseInt(<any>center.x)}x${parseInt(<any>center.y)}`;
     }
     */
}
