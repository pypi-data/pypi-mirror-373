import { BehaviorSubject, Observable, Subject } from "rxjs";
import { filter, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { GridTuple } from "./GridTuple";
import { PrivateDiagramGridLoaderServiceA } from "./PrivateDiagramGridLoaderServiceA";

import {
    Payload,
    PayloadEnvelope,
    TupleOfflineStorageNameService,
    TupleSelector,
    TupleStorageFactoryService,
    TupleStorageServiceABC,
    VortexService,
    VortexStatusService,
    TupleStorageBatchSaveArguments,
} from "@synerty/vortexjs";
import { diagramFilt, gridCacheStorageName } from "../PluginNames";
import { GridUpdateDateTuple } from "./GridUpdateDateTuple";
import { PrivateDiagramTupleService } from "../services";
import { EncodedGridTuple } from "./EncodedGridTuple";
import {
    DeviceOfflineCacheService,
    OfflineCacheLoaderStatusTuple,
} from "@peek/peek_core_device";

// ----------------------------------------------------------------------------

let clientGridWatchUpdateFromDeviceFilt = Object.assign(
    { key: "clientGridWatchUpdateFromDevice" },
    diagramFilt,
);

// ----------------------------------------------------------------------------

/** Grid Key Tuple Selector
 *
 * We're using or own storage database, seprate from the typical
 * offline tuple storage. And we're only going to store grids in id.
 *
 * Because of this, we'll extend tuple selector to only return the grid key
 * instead of it's normal ordered tuplename, {} selector.
 *
 * We only need to convert from this class to string, the revers will attemp
 * to convert it back to a real TupleSelector
 *
 * In summary, this is a hack to avoid a little unnesasary bulk.
 */
class GridKeyTupleSelector extends TupleSelector {
    constructor(gridKey: string) {
        super(gridKey, {});
    }

    /** To Ordered Json Str (Override)
     *
     * This method is used by the Tuple Storage to generate the DB Primary Key
     */
    override toOrderedJsonStr(): string {
        return this.name;
    }
}

// ----------------------------------------------------------------------------
/** Grid Cache
 *
 * This class has the following responsibilities:
 *
 * 3) Poll for grids from the local storage (IndexedDB or WebSQL), and:
 * 3.1) Update the cache
 *
 * 4) Poll for grids from the server and:
 * 4.1) Store these back into the local storage
 * 4.2) Update the cache
 *
 */
@Injectable()
export class PrivateDiagramGridLoaderService extends PrivateDiagramGridLoaderServiceA {
    private UPDATE_CHUNK_FETCH_SIZE = 25;

    // Every 10,000 grids from the server
    private SAVE_POINT_ITERATIONS = 10000;

    // Saving the cache after each chunk is so expensive, we only do it every 20 or so
    private chunksSavedSinceLastIndexSave = 0;

    private isReady$ = new BehaviorSubject<boolean>(false);

    private updatesObservable = new Subject<GridTuple[]>();

    private storage: TupleStorageServiceABC;

    // The last set of keys requested from the GridObserver
    private lastWatchedGridKeys: string[] = [];

    // All cached grid dates
    private index: GridUpdateDateTuple = new GridUpdateDateTuple();

    // The queue of grids to cache
    private askServerChunks = [];

    private _statusSubject = new Subject<OfflineCacheLoaderStatusTuple>();
    private _status = new OfflineCacheLoaderStatusTuple();

    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        private tupleService: PrivateDiagramTupleService,
        storageFactory: TupleStorageFactoryService,
        private deviceCacheControllerService: DeviceOfflineCacheService,
    ) {
        super();

        this._status.pluginName = "peek_plugin_diagram";
        this._status.indexName = "Grids";

        this.storage = storageFactory.create(
            new TupleOfflineStorageNameService(gridCacheStorageName),
        );
        this.storage
            .open()
            .then(() => this.loadGridCacheIndex())
            .then(() => this.isReady$.next(true))
            .catch((e) => console.log(`Failed to open grid cache db ${e}`));

        this.setupVortexSubscriptions();

        // This is loaded regardless for the GridLoader
        // this.deviceCacheControllerService.offlineModeEnabled$
        //     .pipe(takeUntil(this.onDestroyEvent))
        //     .pipe(filter((v) => v))
        //     .pipe(first())
        //     .subscribe(() => {
        //         this.initialLoad();
        //     });

        this.deviceCacheControllerService.triggerCachingStartObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((v) => v))
            .subscribe(() => {
                this.askServerForUpdates();
                this._notifyStatus();
            });

        this.deviceCacheControllerService.triggerCachingResumeObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => {
                this._notifyStatus();
                this.askServerForNextUpdateChunk();
            });
    }

    get observable(): Observable<GridTuple[]> {
        return this.updatesObservable;
    }

    isReady(): Promise<boolean> {
        return this.storage.isOpen();
    }

    isReadyObservable(): Observable<boolean> {
        return this.isReady$;
    }

    statusObservable(): Observable<OfflineCacheLoaderStatusTuple> {
        return this._statusSubject;
    }

    status(): OfflineCacheLoaderStatusTuple {
        return this._status;
    }

    /** Update Watched Grids
     *
     * Change the list of grids that the GridObserver is interested in.
     */
    watchGrids(gridKeys: string[]): void {
        this.lastWatchedGridKeys = gridKeys;
    }

    /** Update Watched Grids
     *
     * Change the list of grids that the GridObserver is interested in.
     */
    async loadGrids(
        currentGridUpdateTimes: { [gridKey: string]: string },
        gridKeys: string[],
    ): Promise<void> {
        // Query the local storage for the grids we don't have in the cache
        let gridTuples: GridTuple[] = await this.queryStorageGrids(gridKeys);

        // Now that we have the results from the local storage,
        // we can send to the server.
        for (let gridTuple of gridTuples)
            currentGridUpdateTimes[gridTuple.gridKey] = gridTuple.lastUpdate;

        this.sendWatchedGridsToServer(currentGridUpdateTimes);
    }

    private _notifyStatus(paused: boolean = false): void {
        this._status.lastCheckDate = new Date();
        this._status.paused = paused;
        this._status.initialFullLoadComplete = this.index.initialLoadComplete;

        this._status.loadingQueueCount = Object.values(
            this.index.updateDateByChunkKey,
        ).filter((v) => v == null).length;

        this._statusSubject.next(this._status);
        this.deviceCacheControllerService.updateLoaderCachingStatus(
            this._status,
        );
    }

    private setupVortexSubscriptions(): void {
        // Services don't have destructors, I'm not sure how to unsubscribe.
        this.vortexService
            .createEndpointObservable(this, clientGridWatchUpdateFromDeviceFilt)
            .subscribe((payloadEnvelope: PayloadEnvelope) =>
                this.processChunksFromServer(payloadEnvelope),
            );
    }

    private areWeTalkingToTheServer(): boolean {
        return (
            this.deviceCacheControllerService.offlineModeEnabled &&
            this.vortexStatusService.snapshot.isOnline
        );
    }

    /** Cache All Grids
     *
     * Cache all the grids from the server, into this device.
     */
    private askServerForUpdates(): void {
        this._notifyStatus();
        if (!this.areWeTalkingToTheServer()) return;

        // If we're still caching, then exit
        if (this.askServerChunks.length != 0) {
            this.askServerForNextUpdateChunk();
            return;
        }

        let keysNeedingUpdate: string[] = [];
        let total = 0;
        let start = 0;
        let chunkSize = 5000;

        let complete = () => {
            this._status.totalLoadedCount = total;
            this.queueChunksToAskServer(keysNeedingUpdate);
        };

        // This is one big hoop to avoid memory issues on older iOS devices
        let queueNext = () => {
            const offset = start + chunkSize;
            let ts = new TupleSelector(GridUpdateDateTuple.tupleName, {
                start: start,
                count: offset,
            });
            start += chunkSize;

            console.log(
                "peek-plugin-diagram: Getting GridUpdateDateTuple " +
                    ` from ${start} to ${offset}`,
            );

            this.tupleService.observer
                .pollForTuples(ts)
                .then((tuples: any[]) => {
                    if (!tuples.length) {
                        console.log(
                            "peek-plugin-diagram:" +
                                " Load of GridUpdateDateTuple Complete",
                        );
                        complete();
                        return;
                    }

                    total += tuples.length;
                    this._status.totalLoadedCount = total;

                    for (let item of tuples) {
                        let chunkKey = item[0];
                        let lastUpdate = item[1];

                        if (
                            !this.index.updateDateByChunkKey.hasOwnProperty(
                                chunkKey,
                            )
                        ) {
                            this.index.updateDateByChunkKey[chunkKey] = null;
                            keysNeedingUpdate.push(chunkKey);
                        } else if (
                            this.index.updateDateByChunkKey[chunkKey] !=
                            lastUpdate
                        ) {
                            keysNeedingUpdate.push(chunkKey);
                        }
                    }
                    this._status.lastCheckDate = new Date();
                    this._notifyStatus();
                    setTimeout(() => queueNext(), 0);
                })
                .catch((e) => console.log(`ERROR in cacheAll : ${e}`));
        };
        queueNext();
    }

    /** Queue Chunks To Ask Server
     *
     */
    private queueChunksToAskServer(keysNeedingUpdate: string[]) {
        if (!this.areWeTalkingToTheServer()) return;

        this.askServerChunks = [];
        this.chunksSavedSinceLastIndexSave = 0;

        let count = 0;
        let indexChunk = {};

        for (let key of keysNeedingUpdate) {
            indexChunk[key] = this.index.updateDateByChunkKey[key];
            count++;

            if (count == this.UPDATE_CHUNK_FETCH_SIZE) {
                this.askServerChunks.push(indexChunk);
                count = 0;
                indexChunk = {};
            }
        }

        if (count) this.askServerChunks.push(indexChunk);

        this.askServerForNextUpdateChunk();

        this._status.lastCheckDate = new Date();
        this._notifyStatus();
    }

    /** Cache Request Next Chunk
     *
     * Request the next chunk of grids from the server
     */
    private askServerForNextUpdateChunk() {
        if (!this.areWeTalkingToTheServer()) return;

        if (this.askServerChunks.length == 0) return;

        if (this.deviceCacheControllerService.isOfflineCachingPaused) {
            this.saveChunkCacheIndex(true) //
                .catch((e) => console.log(`ERROR saveChunkCacheIndex: ${e}`));
            this._notifyStatus(true);
            return;
        }

        let nextChunk = this.askServerChunks.pop();

        let payload = new Payload({ cacheAll: true }, [nextChunk]);
        Object.assign(payload.filt, clientGridWatchUpdateFromDeviceFilt);
        this.vortexService.sendPayload(payload);

        this._status.lastCheckDate = new Date();
        this._notifyStatus();
    }

    //
    private sendWatchedGridsToServer(updateTimeByGridKey: {
        [gridKey: string]: string;
    }) {
        // There is no point talking to the server if it's offline
        if (!this.vortexStatusService.snapshot.isOnline) return;

        let payload = new Payload(clientGridWatchUpdateFromDeviceFilt);
        payload.tuples = [updateTimeByGridKey];
        this.vortexService.sendPayload(payload);
    }

    /** Process Grids From Server
     *
     * Process the grids the server has sent us.
     */
    private async processChunksFromServer(
        payloadEnvelope: PayloadEnvelope,
    ): Promise<void> {
        if (
            (payloadEnvelope.result != null &&
                payloadEnvelope.result != true) ||
            payloadEnvelope.data == null
        ) {
            console.log(`ERROR: ${payloadEnvelope.result}`);
            return;
        }

        const tuplesToSave: EncodedGridTuple[] = <EncodedGridTuple[]>(
            payloadEnvelope.data
        );

        let isCacheAll = payloadEnvelope.filt["cacheAll"] === true;

        if (!isCacheAll) {
            this.emitEncodedGridTuples(tuplesToSave);
        }

        try {
            await this.storeChunkTuples(tuplesToSave);
        } catch (e) {
            console.log(`ERROR GridLoader.processGridsFromServer: ${e}`);
        }

        // We always cache the tuples
        if (!isCacheAll) return;

        this.chunksSavedSinceLastIndexSave += tuplesToSave.length;

        if (this.askServerChunks.length == 0) {
            this.index.initialLoadComplete = true;
            await this.saveChunkCacheIndex(true);
        } else {
            this.askServerForNextUpdateChunk();
        }
        this._notifyStatus();
    }

    /** Store Grid Tuples
     * This is called with grids from the server, store them for later.
     */
    private async storeChunkTuples(
        tuplesToSave: EncodedGridTuple[],
    ): Promise<void> {
        // noinspection BadExpressionStatementJS
        const Selector = GridKeyTupleSelector;

        if (tuplesToSave.length == 0) return;

        const gridKeys = [];
        for (let encodedGridTuple of tuplesToSave) {
            gridKeys.push(encodedGridTuple.chunkKey);
        }
        console.log(`Caching grids ${gridKeys}`);

        const batchStore: TupleStorageBatchSaveArguments[] = [];
        for (let encodedGridTuple of tuplesToSave) {
            if (encodedGridTuple.encodedData == null) {
                await this.storage.deleteTuples(
                    new Selector(encodedGridTuple.chunkKey),
                );
                delete this.index.updateDateByChunkKey[
                    encodedGridTuple.chunkKey
                ];
            } else {
                batchStore.push({
                    tupleSelector: new Selector(encodedGridTuple.chunkKey),
                    vortexMsg: encodedGridTuple.encodedData,
                });
            }
        }
        await this.storage.batchSaveTuplesEncoded(batchStore);

        for (let encodedGridTuple of tuplesToSave) {
            if (encodedGridTuple.encodedData != null) {
                this.index.updateDateByChunkKey[encodedGridTuple.chunkKey] =
                    encodedGridTuple.lastUpdate;
            }
        }

        await this.saveChunkCacheIndex(false);
    }

    /** Store Grid Cache Index
     *
     * Updates our running tab of the update dates of the cached grids
     *
     */
    private async saveChunkCacheIndex(force = false): Promise<void> {
        if (
            this.chunksSavedSinceLastIndexSave <= this.SAVE_POINT_ITERATIONS &&
            !force
        )
            return;

        const ts = new TupleSelector(GridUpdateDateTuple.tupleName, {});

        this.chunksSavedSinceLastIndexSave = 0;

        return await this.storage.saveTuples(ts, [this.index]);
    }

    private emitEncodedGridTuples(encodedGridTuples: EncodedGridTuple[]): void {
        let promises: Promise<void>[] = [];
        let gridTuples: GridTuple[] = [];

        for (let encodedGridTuple of encodedGridTuples) {
            if (encodedGridTuple.encodedGridTuple == null) {
                // Add an empty grid
                const gridTuple = new GridTuple();
                gridTuple.gridKey = encodedGridTuple.gridKey;
                gridTuple.dispJsonStr = null;
                gridTuple.lastUpdate = null;
                gridTuples.push(gridTuple);
                promises.push(Promise.resolve());
            } else {
                let promise: any = Payload.fromEncodedPayload(
                    encodedGridTuple.encodedGridTuple,
                )
                    .then((payload: Payload) => {
                        gridTuples.push(payload.tuples[0]);
                    })
                    .catch((err) => {
                        console.log(
                            `GridLoader.emitEncodedGridTuples decode error: ${err}`,
                        );
                    });
                promises.push(promise);
            }
        }

        Promise.all(promises)
            .then(() => {
                this.updatesObservable.next(gridTuples);
            })
            .catch((err) => {
                console.log(
                    `GridLoader.emitEncodedGridTuples all error: ${err}`,
                );
            });
    }

    /** Query Storage Grids
     *
     * Load grids from local storage if they exist in it.
     *
     */
    private async queryStorageGrids(gridKeys: string[]): Promise<GridTuple[]> {
        const promises = [];
        //noinspection JSMismatchedCollectionQueryUpdate
        let gridTuples: GridTuple[] = [];

        for (let gridKey of gridKeys) {
            promises.push(
                this.storage
                    .loadTuples(new GridKeyTupleSelector(gridKey))
                    .then((grids: GridTuple[]) => {
                        // Length should be 0 or 1
                        if (!grids.length) return;
                        gridTuples.push(grids[0]);
                        this.updatesObservable.next(grids);
                    }),
            );
        }

        await Promise.all(promises);

        return gridTuples;
    }

    /** Load Grid Cache Index
     *
     * Loads the running tab of the update dates of the cached grids
     *
     */
    private async loadGridCacheIndex(): Promise<void> {
        let tuples: any[] = await this.storage.loadTuples(
            new TupleSelector(GridUpdateDateTuple.tupleName, {}),
        );
        // Length should be 0 or 1
        if (tuples.length) this.index = tuples[0];
    }
}
