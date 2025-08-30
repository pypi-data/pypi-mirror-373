import { DispBase } from "./DispBase";
import { DispPolyline } from "./DispPolyline";
import { DispPolygon } from "./DispPolygon";
import { DispText } from "./DispText";
import { DispEllipse } from "./DispEllipse";
import { DispGroupPointer } from "./DispGroupPointer";
import { DispGroup } from "./DispGroup";
import { DispNull } from "./DispNull";
import { getWrapper, registerType } from "./DispFactoryTypeMap";
import { DispCurvedText } from "./DispCurvedText";

export class DispFactory {
    private static _typeMapInit = false;

    static wrapper(disp): any {
        if (!DispFactory._typeMapInit) {
            DispFactory._typeMapInit = true;
            registerType(DispBase.TYPE_DT, DispText);
            registerType(DispBase.TYPE_DCT, DispCurvedText);
            registerType(DispBase.TYPE_DPG, DispPolygon);
            registerType(DispBase.TYPE_DPL, DispPolyline);
            registerType(DispBase.TYPE_DE, DispEllipse);
            registerType(DispBase.TYPE_DG, DispGroup);
            registerType(DispBase.TYPE_DGP, DispGroupPointer);
            registerType(DispBase.TYPE_DN, DispNull);
        }
        return getWrapper(disp._tt);
    }
}
