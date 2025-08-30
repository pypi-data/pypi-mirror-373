import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class ShapeTextStyleTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ShapeTextStyleTuple";

    key: string;
    modelSetKey: string;

    name: string;
    fontName: string;
    fontSize: number;
    fontStyle: string | null;
    scalable: boolean;
    scaleFactor: number;
    spacingBetweenTexts: number;
    borderWidth: number;
    showForEdit: boolean;
    wrapTextAtChars: number;
    wrapTextAtCharSplitBetweenWords: boolean;

    constructor() {
        super(ShapeTextStyleTuple.tupleName);
    }
}
