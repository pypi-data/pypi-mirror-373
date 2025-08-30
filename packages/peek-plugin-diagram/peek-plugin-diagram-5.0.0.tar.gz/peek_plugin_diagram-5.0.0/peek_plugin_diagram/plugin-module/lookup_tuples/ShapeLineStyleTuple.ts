import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class ShapeLineStyleTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ShapeLineStyleTuple";

    key: string;
    modelSetKey: string;

    name: string;
    backgroundFillDashSpace: string;

    static readonly CAP_BUTT = "butt";
    static readonly CAP_ROUND = "round";
    static readonly CAP_SQUARE = "square";
    capStyle: string;

    static readonly JOIN_BEVEL = "bevel";
    static readonly JOIN_ROUND = "round";
    static readonly JOIN_MITER = "miter";
    joinStyle: string;

    dashPattern: null | string; // Stored in the DB as a string
    dashPatternParsed: null | number[]; // Parsed when the tuples are loaded

    startArrowSize: number;
    endArrowSize: number;

    // winStyle: number;

    scalable: boolean;

    showForEdit: boolean;

    constructor() {
        super(ShapeLineStyleTuple.tupleName);
    }
}
