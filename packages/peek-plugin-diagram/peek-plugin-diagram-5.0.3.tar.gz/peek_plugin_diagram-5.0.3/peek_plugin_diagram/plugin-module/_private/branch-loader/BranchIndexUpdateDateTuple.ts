import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

@addTupleType
export class BranchIndexUpdateDateTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "BranchIndexUpdateDateTuple";
    initialLoadComplete: boolean = false;
    updateDateByChunkKey: {} = {};
    // Improve performance of the JSON serialisation
    protected override _rawJonableFields = [
        "initialLoadComplete",
        "updateDateByChunkKey",
    ];

    constructor() {
        super(BranchIndexUpdateDateTuple.tupleName);
    }
}
