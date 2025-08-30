import { Observable, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { LinkedGrid } from "./LinkedGrid.web";
import {
    GridTuple,
    PrivateDiagramGridLoaderServiceA,
} from "@peek/peek_plugin_diagram/_private/grid-loader";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { dateStr } from "../DiagramUtil";

class Cache {
    private cache: { [gridKey: string]: LinkedGrid } = {};

    get grids(): LinkedGrid[] {
        const grids = [];
        for (const gridKey of Object.keys(this.cache)) {
            grids.push(this.cache[gridKey]);
        }
        return grids;
    }

    put(grid: LinkedGrid): void {
        this.cache[grid.gridKey] = grid;
    }

    get(gridKey: string): null | LinkedGrid {
        if (!this.has(gridKey)) return null;
        return this.cache[gridKey];
    }

    del(gridKey: string): void {
        delete this.cache[gridKey];
    }

    has(gridKey: string): boolean {
        return this.cache.hasOwnProperty(gridKey);
    }
}

/** Grid Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Keep and manage an in memory dict of grids.
 *
 * 2) Provide updates to the GridObservable class as grid updates come in.
 *
 * 3) Poll for grids from the grid loader
 *
 */
@Injectable()
export class GridCache extends NgLifeCycleEvents {
    private updatesObservable = new Subject<LinkedGrid>();

    // This is the last X number of caches.
    // We will cache the last 20 sets of watched grids in these caches
    // Over 20, will just fall out of scope and be garbage collected
    private cacheQueue: Cache[] = [];
    private MAX_CACHE = 50;

    // TODO, There appears to be no way to tear down a service
    constructor(
        private lookupService: PrivateDiagramLookupService,
        private gridLoader: PrivateDiagramGridLoaderServiceA,
    ) {
        super();

        // Services don't have destructors, I'm not sure how to unsubscribe.
        this.gridLoader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: GridTuple[]) =>
                this.processGridUpdates(tuples),
            );

        // If the lookups reload, we need to relink all the disps
        this.lookupService
            .dispsNeedRelinkingObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.relinkAllLookups());
    }

    get observable(): Observable<LinkedGrid> {
        return this.updatesObservable;
    }

    private get linkedGrids(): LinkedGrid[] {
        const linkedGrids: LinkedGrid[] = [];
        for (const cache of this.cacheQueue) linkedGrids.add(cache.grids);
        return [...new Set(linkedGrids)];
    }

    flushCache(): void {
        this.cacheQueue = [];
    }

    resetAllComputedProperties(): void {
        for (const linkedGrid of this.linkedGrids)
            linkedGrid.resetComputedProperties();
    }

    relinkAllLookups(): void {
        for (const linkedGrid of this.linkedGrids)
            linkedGrid.relinkLookups(this.lookupService);
    }

    isReady(): Promise<boolean> {
        return this.gridLoader.isReady();
    }

    isReadyObservable(): Observable<boolean> {
        return this.gridLoader.isReadyObservable();
    }

    /** Update Watched Grids
     *
     * Change the list of grids that the GridObserver is interested in.
     */
    updateWatchedGrids(gridKeys: string[]): void {
        this.gridLoader.watchGrids(gridKeys);

        // Rotate the grid cache
        let latestCache = this.rotateCache(gridKeys);

        // Get the grids and notify the observer
        for (let linkedGrid of latestCache.grids) {
            console.log(
                `${dateStr()} GridCache: Grid from mem cache : ` +
                    `${linkedGrid.gridKey},  ${linkedGrid.lastUpdate}`,
            );
            this.updatesObservable.next(linkedGrid);
        }

        // This is the list of grids we don't have in the cache and we should
        // as the local storage for
        let gridsToGetFromStorage = [];

        // Create the grid list for the server, we include the dates so it doesn't
        // send us stuff we already have.
        let updateTimeByGridKey: { [gridKey: string]: string } = {};
        for (let gridKey of gridKeys) {
            let grid = latestCache.get(gridKey);
            updateTimeByGridKey[gridKey] =
                grid == null ? null : grid.lastUpdate;

            if (grid == null) gridsToGetFromStorage.push(gridKey);
        }

        // Query the local storage for the grids we don't have in the cache
        this.gridLoader.loadGrids(updateTimeByGridKey, gridsToGetFromStorage);
    }

    /** Rotate Cache
     *
     * Instead of managing a pool of objects and determining how long they have been
     * in memory, We'll do this another way.
     *
     * We'll have X number of cache indexes, and the oldest cache drops off
     * the queue. When this happens the garbage collector will clean it up.
     *
     * The overhead is this code and X dict objects.
     */
    private rotateCache(gridKeys: string[]): Cache {
        // let printCache = () => {
        //     for (let i = 0; i < this.cacheQueue.length; i++) {
        //         let cache = this.cacheQueue[i];
        //         console.log(`========================== CACHE ${i}`);
        //         console.log(cache.grids.map((g) => g.gridKey);
        //     }
        // };
        // printCache();

        // Create the latest cache
        let latestCache = new Cache();

        // Populate the latest cache with any grids in previos caches
        for (const gridKey of gridKeys) {
            for (const cache of this.cacheQueue) {
                let thisLinkedGrid = cache.get(gridKey);
                // We're iterating the caches from newest to oldest
                // So we can stop on first hit.
                if (thisLinkedGrid != null) {
                    latestCache.put(thisLinkedGrid);
                    break;
                }
            }
        }

        // Push the latest cache to the front of the queue, if we created it
        this.cacheQueue.unshift(latestCache);

        // Trim the cache
        while (this.cacheQueue.length > this.MAX_CACHE) this.cacheQueue.pop();

        // printCache();

        // Return the latest cache
        return latestCache;
    }

    /** Process Grid Updates
     *
     */
    private processGridUpdates(gridTuples: GridTuple[]) {
        if (this.cacheQueue.length == 0) this.rotateCache([]);

        const latestCache = this.cacheQueue[0];

        for (let gridTuple of gridTuples) {
            let cachedLinkedGrid = null;
            if (gridTuple.dispJsonStr != null) {
                cachedLinkedGrid = latestCache.get(gridTuple.gridKey);
            } else {
                this.clearGridFromCache(gridTuple.gridKey);
            }

            // If the cache differs, ignore the update
            // This really shouldn't happen.
            if (
                cachedLinkedGrid != null &&
                cachedLinkedGrid.lastUpdate == gridTuple.lastUpdate
            ) {
                continue;
            }

            // 1) Link the grid
            let linkedGrid = new LinkedGrid(gridTuple, this.lookupService);

            // 2) Cache the grid
            latestCache.put(linkedGrid);

            // 3) Notify the observer
            this.updatesObservable.next(linkedGrid);
        }
    }

    /** Clear Grid From Cache
     *
     * Remove the gridKey from all of the cache.
     *
     * @param gridKey: The gridKey of the grid to clear
     * @private
     */
    private clearGridFromCache(gridKey: string): void {
        for (let cache of this.cacheQueue) {
            cache.del(gridKey);
        }
    }
}
