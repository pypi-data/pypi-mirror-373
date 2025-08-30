import {filter, first, takeUntil} from "rxjs/operators";
import {Injectable} from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleSelector,
    VortexStatusService,
} from "@synerty/vortexjs";
import {PrivateDiagramTupleService} from "./PrivateDiagramTupleService";
import {GroupDispsTuple, ModelCoordSet, ModelSet} from "../tuples";
import {
    DispColor,
    DispLayer,
    DispLevel,
    DispLineStyle,
    DispTextStyle,
} from "../lookups";
import {BranchKeyToIdMapTuple} from "../branch/BranchKeyToIdMapTuple";
import {BranchService} from "@peek/peek_plugin_branch";
import {Subject} from "rxjs";
import {DeviceEnrolmentService} from "@peek/peek_core_device";

/** Diagram Lookups offline cacher
 *
 * This Service is never unloaded, it makes sure that the lookups that the diagram
 * needs are always stored in the local DB.
 *
 * For NS, This is where the embedded web version reads it from.
 *
 */
@Injectable()
export class PrivateDiagramOfflineCacherService extends NgLifeCycleEvents {
    private static readonly LookupTuples = [
        DispLevel,
        DispLayer,
        DispColor,
        DispTextStyle,
        DispLineStyle,
    ];

    private branchesUnsubUnsubSubject = new Subject<void>();
    private lookupUnsubSubject = new Subject<void>();
    private dispGroupUnsubSubject = new Subject<void>();

    constructor(
        private tupleService: PrivateDiagramTupleService,
        private vortexStatusService: VortexStatusService,
        private globalBranchService: BranchService,
        deviceEnrolmentService: DeviceEnrolmentService,
    ) {
        super();

        // NOTE: This plugin is not loaded for office in plugin_package.json
        if (deviceEnrolmentService.isFieldService) {
            this.initialLoad();
        }
    }

    private initialLoad() {
        // This must be loaded only once

        // Delete data older than 7 days
        let date7DaysAgo = new Date(Date.now() - 7 * 24 * 3600 * 1000);

        let promise = null;
        if (this.vortexStatusService.snapshot.isOnline) {
            promise = this.tupleService.offlineStorage
                .deleteOldTuples(date7DaysAgo)
                .catch((err) =>
                    console.log(`ERROR: Failed to delete old tuples`),
                );
        } else {
            this.vortexStatusService.isOnline
                .pipe(takeUntil(this.onDestroyEvent))
                .pipe(filter((val) => val === true))
                .pipe(first())
                .subscribe(() => {
                    this.tupleService.offlineStorage
                        .deleteOldTuples(date7DaysAgo)
                        .catch((err) =>
                            console.log(`ERROR: Failed to delete old tuples`),
                        );
                });
            promise = Promise.resolve();
        }

        promise.then(() => {
            this.loadModelSet();
            this.loadModelCoordSet();
            this.loadBranchToIdMap();
        });
    }

    /**
     * Cache Model Set
     *
     * This method caches the model set list for offline use.
     *
     */
    private loadModelSet() {
        let tupleSelector = new TupleSelector(ModelSet.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((modelSets: ModelSet[]) => {
                this.branchesUnsubUnsubSubject.next();
                this.tupleService.offlineObserver.flushCache(tupleSelector);
                this.loadLookups(modelSets);

                for (let modelSet of modelSets) {
                    // HACK!!!
                    // force the global branch service to cache it's stuff
                    this.globalBranchService
                        .branches$(modelSet.key)
                        .pipe(
                            takeUntil(this.onDestroyEvent),
                            takeUntil(this.branchesUnsubUnsubSubject)
                        )
                        .subscribe(() => null);
                }
            });
    }

    /**
     * Cache Model Set
     *
     * This method caches the coord sets
     *
     */
    private loadModelCoordSet() {
        let tupleSelector = new TupleSelector(ModelCoordSet.tupleName, {});

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: ModelCoordSet[]) => {
                this.loadDispGroupsAndEdgeTemplates(tuples);
                this.tupleService.offlineObserver.flushCache(tupleSelector);
            });
    }

    /**
     * Cache Branch KeyToIdMap Tuple
     *
     * This method caches the coord sets
     *
     */
    private loadBranchToIdMap() {
        let tupleSelector = new TupleSelector(
            BranchKeyToIdMapTuple.tupleName,
            {},
        );

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: BranchKeyToIdMapTuple[]) => {
                this.tupleService.offlineObserver.flushCache(tupleSelector);
            });
    }

    /**
     * Cache Lookups
     *
     * This method caches the lookups for a model set
     *
     */
    private loadLookups(modelSets: ModelSet[]) {
        this.lookupUnsubSubject.next();

        for (let modelSet of modelSets) {
            for (let LookupTuple of PrivateDiagramOfflineCacherService.LookupTuples) {
                let tupleSelector = new TupleSelector(LookupTuple.tupleName, {
                    modelSetKey: modelSet.key,
                });

                this.tupleService.offlineObserver
                    .subscribeToTupleSelector(tupleSelector)
                    .pipe(
                        takeUntil(this.onDestroyEvent),
                        takeUntil(this.lookupUnsubSubject)
                    )
                    .subscribe((tuples: any[]) => {
                        this.tupleService.offlineObserver.flushCache(
                            tupleSelector,
                        );
                    });
            }
        }
    }

    /**
     * Load Disp Groups
     *
     * This method caches the DispGroups for coord sets.
     *
     */
    private loadDispGroupsAndEdgeTemplates(coordSets: ModelCoordSet[]) {
        this.dispGroupUnsubSubject.next();
        for (let coordSet of coordSets) {
            if (
                !(
                    coordSet.dispGroupTemplatesEnabled ||
                    coordSet.edgeTemplatesEnabled
                )
            ) {
                continue;
            }

            let tupleSelector = new TupleSelector(GroupDispsTuple.tupleName, {
                coordSetId: coordSet.id,
            });

            this.tupleService.offlineObserver
                .subscribeToTupleSelector(tupleSelector)
                .pipe(
                    takeUntil(this.onDestroyEvent),
                    takeUntil(this.dispGroupUnsubSubject)
                )
                .subscribe((tuples: any[]) => {
                    this.tupleService.offlineObserver.flushCache(tupleSelector);
                });
        }
    }
}
