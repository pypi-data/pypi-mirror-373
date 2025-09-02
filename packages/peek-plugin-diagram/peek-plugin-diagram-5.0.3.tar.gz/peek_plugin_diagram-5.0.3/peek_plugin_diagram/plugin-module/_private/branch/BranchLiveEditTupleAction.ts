import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";
import { BranchTuple } from "./BranchTuple";

/** Branch Update Tuple Action
 *
 * This private action is used to transfer updates from the browser to the server.
 *
 */
@addTupleType
export class BranchLiveEditTupleAction extends TupleActionABC {
    public static readonly tupleName =
        diagramTuplePrefix + "BranchLiveEditTupleAction";

    static readonly EDITING_STARTED = 1;
    static readonly EDITING_UPDATED = 2;
    static readonly EDITING_FINISHED = 3;
    static readonly EDITING_SAVED = 4;

    updatedByUser: string = null;
    actionType: number = null;
    branchTuple: BranchTuple = null;

    constructor() {
        super(BranchLiveEditTupleAction.tupleName);
    }
}
