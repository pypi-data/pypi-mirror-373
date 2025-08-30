import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { ShapeTextStyleTuple } from "@peek/peek_plugin_diagram/lookup_tuples";

@addTupleType
export class DispTextStyle extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispTextStyle";

    // Tuple Fields
    key: string;
    modelSetKey: string;

    id: number;
    name: string;

    importHash: string;
    showForEdit: boolean;
    blockApiUpdate: boolean;

    fontName: string;
    fontSize: number;
    fontStyle: string | null;
    scalable: boolean;
    scaleFactor: number;
    modelSetId: number;
    spacingBetweenTexts: number;
    borderWidth: number;
    wrapTextAtChars: number;
    wrapTextAtCharSplitBetweenWords: boolean;

    constructor() {
        super(DispTextStyle.tupleName);
    }

    toTuple(): ShapeTextStyleTuple {
        const tuple_ = new ShapeTextStyleTuple();
        tuple_.key = this.key;
        tuple_.modelSetKey = this.modelSetKey;

        tuple_.name = this.name;
        tuple_.showForEdit = this.showForEdit;

        tuple_.fontName = this.fontName;
        tuple_.fontSize = this.fontSize;
        tuple_.fontStyle = this.fontStyle;
        tuple_.scalable = this.scalable;
        tuple_.scaleFactor = this.scaleFactor;
        tuple_.spacingBetweenTexts = this.spacingBetweenTexts;
        tuple_.borderWidth = this.borderWidth;
        tuple_.wrapTextAtChars = this.wrapTextAtChars;

        return tuple_;
    }
}
