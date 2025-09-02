import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class LocationIndexTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "LocationIndexTuple";

    modelSetKey: string;
    indexBucket: string;

    // The json string.
    jsonStr: string | null;
    lastUpdate: string;

    constructor() {
        super(LocationIndexTuple.tupleName);
    }
}
