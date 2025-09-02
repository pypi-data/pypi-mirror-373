import { Injectable } from "@angular/core";
import { GridCache } from "./GridCache.web";
import { LinkedGrid } from "./LinkedGrid.web";
import { Observable, Subject } from "rxjs";
import { assert, dictKeysFromObject } from "../DiagramUtil";

/** Grid Observable
 *
 * This class keeps track of the different diagram models that are observing grid updates
 *
 * When a grid update comes in from the cache, this class will notify the relevent models.
 *
 */
@Injectable()
export class GridObservable {
    private subjectByCanvasId: { [canvasId: number]: Subject<LinkedGrid> } = {};
    private gridKeysByCanvasId: { [canvasId: number]: string[] } = {};
    private canvasIdsByGidKey: { [gridKey: string]: number[] } = {};

    private lastObservedKeysStr = "";

    constructor(private gridCache: GridCache) {
        // This is a global service, there is no point at which this will unsubscribe
        this.gridCache.observable.subscribe((grid: LinkedGrid) =>
            this.processGridUpdates(grid),
        );
    }

    isReady(): Promise<boolean> {
        return this.gridCache.isReady();
    }

    isReadyObservable(): Observable<boolean> {
        return this.gridCache.isReadyObservable();
    }

    /** Unsubscribe Canvas.
     *
     * The canvas component must call this to tear down and release resources used
     * for it.
     */
    unsubscribeCanvas(canvasId: number): void {
        /* 1) Delete the Subject
         * 2) Update the data structures
         * 3) Notify the grid cache
         */
        delete this.gridKeysByCanvasId[canvasId];
        delete this.subjectByCanvasId[canvasId];
        this.rebuildReverseLookup();
        this.updateGridCacheWatchedKeys();
    }

    observableForCanvas(canvasId: number): Subject<LinkedGrid> {
        // Each canvas should only request the subject once
        assert(
            !this.subjectByCanvasId.hasOwnProperty(canvasId),
            `Canvas ${canvasId} has already requested a subject`,
        );

        this.subjectByCanvasId[canvasId] = new Subject<LinkedGrid>();
        return this.subjectByCanvasId[canvasId];
    }

    updateDiagramWatchedGrids(
        canvasId: number,
        gridKeys: string[],
        forceCacheFlush = false,
    ): void {
        if (forceCacheFlush) {
            this.gridCache.flushCache();
            this.lastObservedKeysStr = "";
        }

        this.gridKeysByCanvasId[canvasId] = gridKeys;
        this.rebuildReverseLookup();
        this.updateGridCacheWatchedKeys();
    }

    resetAllDispComputedProperties(): void {
        this.gridCache.resetAllComputedProperties();
    }

    private processGridUpdates(grid: LinkedGrid) {
        // If we have nothing waiting for this grid, Just disregard it.
        if (!this.canvasIdsByGidKey.hasOwnProperty(grid.gridKey)) return;

        // Notify the subjects for the cavases watching this grid key
        let canvasIds = this.canvasIdsByGidKey[grid.gridKey];
        for (let canvasId of canvasIds) {
            this.subjectByCanvasId[canvasId].next(grid);
        }
    }

    private updateGridCacheWatchedKeys() {
        let uniqueKeysList = dictKeysFromObject(this.canvasIdsByGidKey).sort();
        let uniqueKeysStr = uniqueKeysList.join(",");

        if (this.lastObservedKeysStr == uniqueKeysStr) return;

        this.lastObservedKeysStr = uniqueKeysStr;
        this.gridCache.updateWatchedGrids(uniqueKeysList);
    }

    private rebuildReverseLookup() {
        let newDict = {};

        // Iterate through the canvasIds
        for (let canvasId of dictKeysFromObject(this.gridKeysByCanvasId)) {
            let gridKeys = this.gridKeysByCanvasId[canvasId];

            // Iterate through the gridKeyTuples
            for (let gridKey of gridKeys) {
                // Get the existing array or create one
                let array: any[] = null;
                if (newDict.hasOwnProperty(gridKey)) {
                    array = newDict[gridKey];
                } else {
                    newDict[gridKey] = array = [];
                }
                // Add the item to the array
                array.push(canvasId);
            }
        }

        // Assign the recompiled value back to the class variable
        this.canvasIdsByGidKey = newDict;
    }
}
