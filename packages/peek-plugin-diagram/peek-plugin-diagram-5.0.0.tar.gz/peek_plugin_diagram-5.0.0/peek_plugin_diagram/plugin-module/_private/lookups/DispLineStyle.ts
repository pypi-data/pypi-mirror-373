import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { ShapeLineStyleTuple } from "@peek/peek_plugin_diagram/lookup_tuples";

@addTupleType
export class DispLineStyle extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispLineStyle";

    // Tuple Fields
    key: string;
    modelSetKey: string;

    id: number;
    name: string;

    importHash: string;
    showForEdit: boolean;
    blockApiUpdate: boolean;

    backgroundFillDashSpace: string;

    readonly CAP_BUTT = "butt";
    readonly CAP_ROUND = "round";
    readonly CAP_SQUARE = "square";
    capStyle: string;

    readonly JOIN_BEVEL = "bevel";
    readonly JOIN_ROUND = "round";
    readonly JOIN_MITER = "miter";
    joinStyle: string;

    dashPattern: null | string; // Stored in the DB as a string
    dashPatternParsed: null | number[]; // Parsed when the tuples are loaded

    startArrowSize: number;
    endArrowSize: number;

    // winStyle: number;

    modelSetId: number;

    scalable: boolean;

    constructor() {
        super(DispLineStyle.tupleName);
    }

    toTuple(): ShapeLineStyleTuple {
        const tuple_ = new ShapeLineStyleTuple();
        tuple_.key = this.key;
        tuple_.modelSetKey = this.modelSetKey;

        tuple_.name = this.name;
        tuple_.showForEdit = this.showForEdit;

        tuple_.backgroundFillDashSpace = this.backgroundFillDashSpace;
        tuple_.capStyle = this.capStyle;
        tuple_.joinStyle = this.joinStyle;
        tuple_.dashPattern = this.dashPattern;
        tuple_.dashPatternParsed = this.dashPatternParsed;
        tuple_.startArrowSize = this.startArrowSize;
        tuple_.endArrowSize = this.endArrowSize;
        tuple_.scalable = this.scalable;

        return tuple_;
    }
}
