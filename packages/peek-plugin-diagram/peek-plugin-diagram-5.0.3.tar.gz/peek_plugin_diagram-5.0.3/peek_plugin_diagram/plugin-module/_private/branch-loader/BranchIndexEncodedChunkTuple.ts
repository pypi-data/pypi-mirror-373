import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

@addTupleType
export class BranchIndexEncodedChunkTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "BranchIndexEncodedChunkTuple";

    chunkKey: string;
    lastUpdate: string;
    encodedData: string;

    constructor() {
        super(BranchIndexEncodedChunkTuple.tupleName);
    }
}
