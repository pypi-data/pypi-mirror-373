import { Observable, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { BranchTuple } from "./BranchTuple";
import { BranchLiveEditTupleAction } from "./BranchLiveEditTupleAction";
import { UserListItemTuple } from "@peek/peek_core_user";
import { LocalBranchStorageService } from "../branch-loader/LocalBranchStorageService";
import { BranchUpdateTupleAction } from "./BranchUpdateTupleAction";
import { PrivateDiagramTupleService } from "../services";
import { TupleSelector, VortexStatusService } from "@synerty/vortexjs";
import { BranchLiveEditTuple } from "./BranchLiveEditTuple";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { PrivateDiagramLookupService } from "../services/PrivateDiagramLookupService";

/** Diagram Branch Service
 *
 * This is the implementation of the diagram branch service.
 *
 */
export class PrivateDiagramBranchContext {
    private static readonly SEND_UPDATE_PERIOD = 2000;
    private readonly shutdownSubject = new Subject<void>();
    private readonly _branchUpdatedSubject = new Subject<boolean>();
    private updateTimerNum = null;
    private needsLiveUpdateSend = false;

    constructor(
        private vortexStatusService: VortexStatusService,
        private balloonMsg: BalloonMsgService,
        private lookupCache: PrivateDiagramLookupService,
        private branch: BranchTuple,
        private _modelSetId: number,
        private _modelSetKey: string,
        private _coordSetKey: string,
        private tupleService: PrivateDiagramTupleService,
        private branchLocalLoader: LocalBranchStorageService,
        private userDetails: UserListItemTuple,
    ) {}

    get branchTuple(): BranchTuple {
        return this.branch;
    }

    get modelSetKey(): string {
        return this._modelSetKey;
    }

    get coordSetKey(): string {
        return this._coordSetKey;
    }

    get key(): string {
        return this.branch.key;
    }

    /** Branch Update Observable
     *
     * The observable will be emitted with an
     */
    get branchUpdatedObservable(): Observable<boolean> {
        return this._branchUpdatedSubject.pipe(takeUntil(this.shutdownSubject));
    }

    async save(): Promise<void> {
        this.branchTuple.branchHasBeenSaved();

        await this.branchLocalLoader.saveBranch(this);

        let action = new BranchUpdateTupleAction();
        action.modelSetId = this._modelSetId;
        action.branchTuple = this.branch;
        await this.tupleService.offlineAction.pushAction(action);

        // No need to send a live update, the server will do this when it gets
        // the save action
    }

    open(): void {
        this.sendLiveUpdate(BranchLiveEditTupleAction.EDITING_STARTED);
        this.branch.setContextUpdateCallback((modelUpdateRequired) => {
            this._branchUpdatedSubject.next(modelUpdateRequired);
            this.needsLiveUpdateSend = true;
        });

        let ts = new TupleSelector(BranchLiveEditTuple.tupleName, {
            coordSetId: this.branch.coordSetId,
            key: this.branch.key,
        });

        this.tupleService.observer
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.shutdownSubject))
            .subscribe((tuples: BranchLiveEditTuple[]) => {
                if (tuples.length == 0) return;

                const update = tuples[0];

                if (
                    update.updateFromSave &&
                    update.updatedByUser != this.userKey()
                ) {
                    this.balloonMsg.showWarning(
                        "Another user has saved this diagram edit.",
                    );
                }

                if (update.updateFromSave) {
                    this.branchLocalLoader
                        .saveBranch(this)
                        .catch((e) =>
                            console.log(
                                `Failed to locally save update from server: ${e}`,
                            ),
                        );
                }

                if (this.branch.applyLiveUpdate(update)) {
                    this.branch.linkDisps(this.lookupCache);
                    this._branchUpdatedSubject.next(true);
                }
            });

        this.updateTimerNum = setInterval(() => {
            if (this.needsLiveUpdateSend == false) return;
            this.needsLiveUpdateSend = false;
            this.sendLiveUpdate();
        }, PrivateDiagramBranchContext.SEND_UPDATE_PERIOD);

        this.lookupCache
            .dispsNeedRelinkingObservable()
            .pipe(takeUntil(this.shutdownSubject))
            .subscribe(() => this.branchTuple.linkDisps(this.lookupCache));
    }

    close(): void {
        clearTimeout(this.updateTimerNum);
        this.sendLiveUpdate(BranchLiveEditTupleAction.EDITING_FINISHED);
        this.branch.setContextUpdateCallback(null);
        this.shutdownSubject.next();
    }

    setVisible(visible: boolean): void {
        this.branch.visible = visible;
    }

    private sendLiveUpdate(updateType: number | null = null): void {
        if (updateType == null)
            updateType = BranchLiveEditTupleAction.EDITING_UPDATED;

        let action = new BranchLiveEditTupleAction();
        action.updatedByUser = this.userKey();
        action.branchTuple = this.branch;
        action.branchTuple.updatedByUser = this.userKey();
        action.actionType = updateType;

        let promise = null;
        if (updateType == BranchLiveEditTupleAction.EDITING_UPDATED) {
            // All updates are only sent when the device is online
            if (this.vortexStatusService.snapshot.isOnline)
                promise = this.tupleService.action.pushAction(action);
        } else {
            // ALL Start and Finish updates are sent
            promise = this.tupleService.offlineAction.pushAction(action);
        }

        if (promise != null) {
            promise.catch((e) =>
                console.log(`Failed to send live update for branch: ${e}`),
            );
        }
    }

    private userKey(): string {
        return `${this.userDetails.userTitle} (${this.userDetails.userName})`;
    }
}
