import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

@addTupleType
export class EncodedGridTuple extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "EncodedGridTuple";

    gridKey: string;
    // A GridTuple, already encoded and ready for storage in the clients cache
    encodedGridTuple: string | null;
    lastUpdate: string;

    // This is populated when the grid gets to the client.
    // This way, when the grid is stored in tuple storage, there only needs to be one
    // string inflate (decompress)
    dispJsonStr: string | null;

    // As per dispJsonStr, but for branches
    branchJsonStr: string | null;

    constructor() {
        super(EncodedGridTuple.tupleName);
    }

    get chunkKey(): string {
        return this.gridKey;
    }

    get encodedData(): string | null {
        return this.encodedGridTuple;
    }
}
