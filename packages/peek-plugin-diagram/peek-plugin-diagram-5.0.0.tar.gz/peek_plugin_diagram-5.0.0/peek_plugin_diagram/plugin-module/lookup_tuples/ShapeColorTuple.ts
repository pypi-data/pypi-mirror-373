import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class ShapeColorTuple extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "ShapeColorTuple";

    key: string;
    modelSetKey: string;
    name: string;
    altColor: string | null;
    swapPeriod: number | null;
    showForEdit: boolean;

    darkColor: string;
    lightColor: string;

    constructor() {
        super(ShapeColorTuple.tupleName);
    }

    getColor(isLightMode: boolean): string {
        return isLightMode ? this.lightColor : this.darkColor;
    }
}
