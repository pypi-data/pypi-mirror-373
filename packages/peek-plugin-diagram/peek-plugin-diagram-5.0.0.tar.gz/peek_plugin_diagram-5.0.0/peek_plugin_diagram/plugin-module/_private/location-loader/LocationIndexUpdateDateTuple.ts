import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class LocationIndexUpdateDateTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "LocationIndexUpdateDateTuple";

    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};

    constructor() {
        super(LocationIndexUpdateDateTuple.tupleName);
    }
}
