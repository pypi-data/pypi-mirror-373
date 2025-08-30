import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

/** Branch Key to ID Map Tuple
 *
 * This tuple is used by the UI to get the IDs for branches for the
 * model compiler to enable branches.
 *
 */
@addTupleType
export class BranchKeyToIdMapTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "BranchKeyToIdMapTuple";

    coordSetId: number;
    keyIdMap: { [key: string]: number };

    constructor() {
        super(BranchKeyToIdMapTuple.tupleName);
    }
}
