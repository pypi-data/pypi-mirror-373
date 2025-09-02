import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { LocationIndexTuple } from "./LocationIndexTuple";

@addTupleType
export class EncodedLocationIndexTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "EncodedLocationIndexTuple";

    modelSetKey: string;
    indexBucket: string;

    // The LocationIndexTuple pre-encoded to a Payload
    encodedLocationIndexTuple: string = null;
    lastUpdate: string;

    constructor() {
        super(EncodedLocationIndexTuple.tupleName);
    }

    get chunkKey(): string {
        return this.indexBucket;
    }

    get encodedData(): string {
        return this.encodedLocationIndexTuple;
    }
}
