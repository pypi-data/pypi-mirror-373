import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";
import { BranchTuple } from "./BranchTuple";

/** Branch Update Tuple Action
 *
 * This private action is used to transfer updates from the browser to the server.
 *
 */
@addTupleType
export class BranchUpdateTupleAction extends TupleActionABC {
    public static readonly tupleName =
        diagramTuplePrefix + "BranchUpdateTupleAction";

    doDelete: boolean = false;
    modelSetId: number = null;
    branchTuple: BranchTuple = null;

    constructor() {
        super(BranchUpdateTupleAction.tupleName);
    }
}
