import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";
import { BranchTuple } from "./BranchTuple";
import { BranchLiveEditTupleAction } from "./BranchLiveEditTupleAction";

/** Branch Live Edit Tuple
 *
 * This tuple is used internally to transfer branches between UIs that are actively
 * editing the.
 *
 * This isn't stored anywhere, it just gets relayed between multiple UIs.
 *
 */
@addTupleType
export class BranchLiveEditTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "BranchLiveEditTuple";

    EDITING_STARTED = BranchLiveEditTupleAction.EDITING_STARTED;
    EDITING_UPDATED = BranchLiveEditTupleAction.EDITING_UPDATED;
    EDITING_FINISHED = BranchLiveEditTupleAction.EDITING_FINISHED;
    EDITING_SAVED = BranchLiveEditTupleAction.EDITING_SAVED;

    branchTuple: BranchTuple = null;
    updatedByUser: string = null;

    uiUpdateDate: Date = null;
    serverUpdateDate: Date = null;

    updateFromActionType: number = null;

    constructor() {
        super(BranchLiveEditTuple.tupleName);
    }

    get updateFromSave(): boolean {
        return this.updateFromActionType === this.EDITING_SAVED;
    }
}
