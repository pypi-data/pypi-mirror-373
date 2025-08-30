import { Observable, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { PrivateDiagramBranchContext } from "../branch/PrivateDiagramBranchContext";
import { BranchTuple } from "../branch/BranchTuple";
import { BranchIndexLoaderServiceA } from "../branch-loader/BranchIndexLoaderServiceA";
import { DiagramCoordSetService } from "../../DiagramCoordSetService";
import { LocalBranchStorageService } from "../branch-loader/LocalBranchStorageService";
import { BranchIndexResultI } from "../branch-loader/BranchIndexLoaderService";
import { ModelCoordSet } from "../tuples";
import {
    PrivateDiagramCoordSetService,
    PrivateDiagramTupleService,
} from "../services";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleSelector,
    VortexStatusService,
} from "@synerty/vortexjs";
import { BranchKeyToIdMapTuple } from "./BranchKeyToIdMapTuple";
import { BranchDetailTuple } from "@peek/peek_plugin_branch";
import { UserService } from "@peek/peek_core_user";
import { DiagramBranchDetailsI } from "../../DiagramBranchService";
import { PrivateDiagramLookupService } from "../services/PrivateDiagramLookupService";
import * as moment from "moment";

export interface PopupEditBranchSelectionArgs {
    modelSetKey: string;
    coordSetKey: string;
}

/** Diagram Branch Service
 *
 * This service notifies the popup service that an item has been selected.
 *
 */
@Injectable()
export class PrivateDiagramBranchService extends NgLifeCycleEvents {
    private _startEditingWithContextObservable =
        new Subject<PrivateDiagramBranchContext>();
    private _startEditingObservable = new Subject<void>();
    private _stopEditingObservable = new Subject<void>();
    private _popupEditBranchSelectionSubject: Subject<PopupEditBranchSelectionArgs> =
        new Subject<PopupEditBranchSelectionArgs>();
    private coordSetService: PrivateDiagramCoordSetService;
    private branchIdMapByCoordSetId: {
        [coordSetId: number]: BranchKeyToIdMapTuple;
    } = {};
    private enabledBranches: BranchDetailTuple[] = [];
    private activeBranchContext: PrivateDiagramBranchContext | null = null;

    constructor(
        private vortexStatusService: VortexStatusService,
        private balloonMsg: BalloonMsgService,
        private userService: UserService,
        private lookupService: PrivateDiagramLookupService,
        coordSetService: DiagramCoordSetService,
        private branchLocalLoader: LocalBranchStorageService,
        private branchIndexLoader: BranchIndexLoaderServiceA,
        private tupleService: PrivateDiagramTupleService,
    ) {
        super();

        this.coordSetService = <PrivateDiagramCoordSetService>coordSetService;

        let tupleSelector = new TupleSelector(
            BranchKeyToIdMapTuple.tupleName,
            {},
        );

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: BranchKeyToIdMapTuple[]) => {
                this.branchIdMapByCoordSetId = {};
                for (let tuple of tuples) {
                    this.branchIdMapByCoordSetId[tuple.coordSetId] = tuple;
                }
            });
    }

    /** This observable is subscribed to by the create/edit branch popup */
    get popupEditBranchSelectionObservable(): Observable<PopupEditBranchSelectionArgs> {
        return this._popupEditBranchSelectionSubject;
    }

    areBranchesActive(coordSetId: number): boolean {
        return this.enabledBranches.length != 0;
    }

    getVisibleBranchIds(coordSetId: number): number[] {
        let keyIdMapTuple = this.branchIdMapByCoordSetId[coordSetId];
        if (keyIdMapTuple == null) return [];

        let ids = [];
        for (let branch of this.enabledBranches) {
            let branchId = keyIdMapTuple.keyIdMap[branch.key];
            if (branchId != null) ids.push(branchId);
        }
        return ids;
    }

    getDiagramBranchKeys(coordSetId: number): string[] {
        let keyIdMapTuple = this.branchIdMapByCoordSetId[coordSetId];
        if (keyIdMapTuple == null) return [];

        return Object.keys(keyIdMapTuple.keyIdMap);
    }

    getBranch(
        modelSetKey: string,
        coordSetKey: string,
        branchKey: string,
    ): Promise<PrivateDiagramBranchContext | null> {
        return this._loadBranchContext(
            modelSetKey,
            coordSetKey,
            branchKey,
            false,
        );
    }

    getOrCreateBranch(
        modelSetKey: string,
        coordSetKey: string,
        branchKey: string,
    ): Promise<PrivateDiagramBranchContext> {
        return this._loadBranchContext(
            modelSetKey,
            coordSetKey,
            branchKey,
            true,
        );
    }

    // Layer Select Popup
    /** This method is called from the diagram-toolbar component */
    popupEditBranchSelection(modelSetKey: string, coordSetKey: string): void {
        this._popupEditBranchSelectionSubject.next({
            modelSetKey: modelSetKey,
            coordSetKey: coordSetKey,
        });
    }

    // ---------------

    async startEditing(
        modelSetKey: string,
        coordSetKey: string,
        branchKey: string,
    ): Promise<void> {
        // If we're already editing this branch then do nothing
        if (
            this.activeBranchContext != null &&
            this.activeBranchContext.modelSetKey == modelSetKey &&
            this.activeBranchContext.coordSetKey == coordSetKey &&
            this.activeBranchContext.branchTuple.key == branchKey
        ) {
            return;
        }

        try {
            const context = await this.getOrCreateBranch(
                modelSetKey,
                coordSetKey,
                branchKey,
            );

            this.activeBranchContext = context;
            this._startEditingWithContextObservable.next(context);
            this._startEditingObservable.next();
        } catch (e) {
            this._startEditingWithContextObservable.error(e);
        }
    }

    startEditingWithContextObservable(): Observable<PrivateDiagramBranchContext> {
        return this._startEditingWithContextObservable;
    }

    startEditingObservable(): Observable<void> {
        return this._startEditingObservable;
    }

    stopEditing(): void {
        this.activeBranchContext = null;
        this._stopEditingObservable.next();
    }

    stopEditingObservable(): Observable<void> {
        return this._stopEditingObservable;
    }

    setVisibleBranches(commonBranches: BranchDetailTuple[]): void {
        this.enabledBranches = commonBranches;
    }

    getVisibleBranches(): BranchDetailTuple[] {
        return this.enabledBranches.slice();
    }

    getActiveBranchDetails(): Promise<DiagramBranchDetailsI | null> {
        if (this.activeBranchContext == null) return Promise.resolve(null);

        return Promise.resolve({
            modelSetKey: this.activeBranchContext.modelSetKey,
            coordSetKey: this.activeBranchContext.coordSetKey,
            branchKey: this.activeBranchContext.branchTuple.key,
            updatedByUser: this.activeBranchContext.branchTuple.updatedByUser,
            createdDate: this.activeBranchContext.branchTuple.createdDate,
            updatedDate: this.activeBranchContext.branchTuple.updatedDate,
            anchorKeys: this.activeBranchContext.branchTuple.anchorDispKeys,
        });
    }

    // ========================================================================
    // Methods for the public class

    private _loadBranch(
        modelSetKey: string,
        coordSetKey: string,
        branchKey: string,
    ): Promise<BranchTuple | null> {
        if (!this.coordSetService.isReady())
            throw new Error("CoordSet service is not initialised yet");

        let coordSet: ModelCoordSet = this.coordSetService.coordSetForKey(
            modelSetKey,
            coordSetKey,
        );

        let indexBranch: BranchTuple | null = null;
        let localBranch: BranchTuple | null = null;

        let promises = [];

        // Load the branch from the index
        promises.push(
            this.branchIndexLoader
                .getBranches(modelSetKey, coordSet.id, [branchKey])
                .then((results: BranchIndexResultI) => {
                    // This will be null if it didn't find one.
                    if (results[branchKey] != null)
                        indexBranch = results[branchKey][0];
                }),
        );

        // Load
        promises.push(
            this.branchLocalLoader
                .loadBranch(modelSetKey, coordSet.id, branchKey)
                .then((branch: BranchTuple | null) => {
                    localBranch = branch;
                }),
        );

        let prom: any = Promise.all(promises).then(() => {
            let branch = null;
            if (localBranch != null && indexBranch != null) {
                if (
                    moment(localBranch.updatedDate).isAfter(
                        indexBranch.updatedDate,
                    )
                )
                    branch = localBranch;
                else branch = indexBranch;
            } else if (localBranch != null) {
                branch = localBranch;
            } else if (indexBranch != null) {
                branch = indexBranch;
            } else {
                return null;
            }

            branch.linkDisps(this.lookupService);
            branch.initialiseIndexes();
            return branch;
        });
        return prom;
    }

    private async _loadBranchContext(
        modelSetKey: string,
        coordSetKey: string,
        branchKey: string,
        createIfMissing: boolean,
    ): Promise<PrivateDiagramBranchContext | null> {
        if (!this.coordSetService.isReady())
            throw new Error("CoordSet service is not initialised yet");

        const coordSet: ModelCoordSet = this.coordSetService.coordSetForKey(
            modelSetKey,
            coordSetKey,
        );

        let branch = await this._loadBranch(
            modelSetKey,
            coordSetKey,
            branchKey,
        );

        if (branch == null) {
            if (!createIfMissing) {
                return null;
            }

            branch = BranchTuple.createBranch(coordSet.id, branchKey);
            branch.linkDisps(this.lookupService);
        }

        return new PrivateDiagramBranchContext(
            this.vortexStatusService,
            this.balloonMsg,
            this.lookupService,
            branch,
            coordSet.modelSetId,
            modelSetKey,
            coordSetKey,
            this.tupleService,
            this.branchLocalLoader,
            this.userService.userDetails,
        );
    }
}
