import { Injectable } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageFactoryService,
} from "@synerty/vortexjs";
import { branchLocalStorageName, diagramTuplePrefix } from "../PluginNames";
import { BranchTuple } from "../branch/BranchTuple";
import { PrivateDiagramBranchContext } from "../branch";

// ----------------------------------------------------------------------------
/** LocallyStoredBranchTupleSelector
 *
 * This is just a short cut for the tuple selector
 */
class LocallyStoredBranchTupleSelector extends TupleSelector {
    constructor(
        private modelSetKey: string,
        private key: string,
    ) {
        super(diagramTuplePrefix + "BranchTuple.LocallyStored", {
            modelSetKey: modelSetKey,
            key: key,
        });
    }
}

// ----------------------------------------------------------------------------
/** Local Branch Storage Service
 *
 * This class manages storing of branches locally, this allows branches to
 * be created and edited offline.
 *
 * 1) Maintain a local storage of the BranchTuple
 *
 */
@Injectable()
export class LocalBranchStorageService extends NgLifeCycleEvents {
    private storage: TupleOfflineStorageService;

    constructor(storageFactory: TupleStorageFactoryService) {
        super();

        this.storage = new TupleOfflineStorageService(
            storageFactory,
            new TupleOfflineStorageNameService(branchLocalStorageName),
        );
    }

    /** Get Branch
     *
     * Get the objects with matching key from the index..
     *
     */
    loadBranch(
        modelSetKey: string,
        coordSetId: number,
        key: string,
    ): Promise<BranchTuple | null> {
        let prom: any = this.loadBranches(modelSetKey, key).then(
            (branches: BranchTuple[]) => {
                for (let branch of branches) {
                    if (branch.coordSetId == coordSetId) return branch;
                }
            },
        );
        return prom;
    }

    /** Get Branches
     *
     * Get the branches with the matching
     *
     */
    loadBranches(modelSetKey: string, key: string): Promise<BranchTuple[]> {
        let ts = new LocallyStoredBranchTupleSelector(modelSetKey, key);
        let prom: any = this.storage.loadTuples(ts);

        return prom;
    }

    saveBranch(branchContext: PrivateDiagramBranchContext): Promise<void> {
        let branchToSave: BranchTuple = branchContext["branch"];
        let ts = new LocallyStoredBranchTupleSelector(
            branchContext.modelSetKey,
            branchContext.key,
        );
        let prom: any = this.loadBranches(
            branchContext.modelSetKey,
            branchToSave.key,
        ).then((branches: BranchTuple[]) => {
            // Iterate though and update
            let updated = false;
            for (let i = 0; i < branches.length; i++) {
                if (branches[i].key == branchToSave.key) {
                    branches[i] = branchToSave;
                    updated = true;
                    break;
                }
            }

            // If we couldn't find it, then add it
            if (!updated) branches.push(branchToSave);

            return this.storage.saveTuples(ts, branches);
        });
        return prom;
    }
}
