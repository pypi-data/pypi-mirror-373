import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

/* Group Disps Tuple
 
 This tuple stores a list of DispGroups that are in the 'ID:dispgroup' grid key
 in that coord set.
 
 */
@addTupleType
export class GroupDispsTuple extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "GroupDispsTuple";

    coordSetId: number;

    // A GridTuple, already encoded and ready for storage in the clients cache
    encodedGridTuple: string;

    constructor() {
        super(GroupDispsTuple.tupleName);
    }
}
