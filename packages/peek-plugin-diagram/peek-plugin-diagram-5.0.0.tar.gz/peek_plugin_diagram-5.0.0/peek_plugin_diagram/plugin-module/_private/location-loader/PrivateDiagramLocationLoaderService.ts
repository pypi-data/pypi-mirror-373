import { BehaviorSubject, firstValueFrom, Observable, Subject } from "rxjs";
import { filter, first, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { LocationIndexTuple } from "./LocationIndexTuple";
import {
    NgLifeCycleEvents,
    Payload,
    PayloadEnvelope,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageBatchSaveArguments,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import {
    diagramFilt,
    locationIndexCacheStorageName,
} from "@peek/peek_plugin_diagram/_private";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { LocationIndexUpdateDateTuple } from "./LocationIndexUpdateDateTuple";
import { DispKeyLocationTuple } from "./DispKeyLocationTuple";
import { PrivateDiagramCoordSetService } from "../services/PrivateDiagramCoordSetService";
import { EncodedLocationIndexTuple } from "./EncodedLocationIndexTuple";
import { PrivateDiagramTupleService } from "../services/PrivateDiagramTupleService";
import {
    DeviceOfflineCacheService,
    OfflineCacheLoaderStatusTuple,
} from "@peek/peek_core_device";

// ----------------------------------------------------------------------------

let clientLocationIndexWatchUpdateFromDeviceFilt = Object.assign(
    { key: "clientLocationIndexWatchUpdateFromDevice" },
    diagramFilt,
);

const cacheAll = "cacheAll";

// ----------------------------------------------------------------------------
/** LocationIndexTupleSelector
 */
class LocationIndexTupleSelector extends TupleSelector {
    constructor(indexBucket: string) {
        super(LocationIndexTuple.tupleName, { key: indexBucket });
    }
}

// ----------------------------------------------------------------------------
/** LastUpdateTupleSelector
 */
class UpdateDateTupleSelector extends TupleSelector {
    constructor() {
        super(LocationIndexUpdateDateTuple.tupleName, {});
    }
}

// ----------------------------------------------------------------------------
/** hash method
 */
let BUCKET_COUNT = 1024;

function dispKeyHashBucket(modelSetKey: string, dispKey: string): string {
    /** Disp Key Hash Bucket

     This method create an int from 0 to 255, representing the hash bucket for this
     key.

     This is simple, and provides a reasonable distribution

     @param modelSetKey:
     @param dispKey:

     @return:

     */
    if (modelSetKey == null || modelSetKey.length == 0)
        throw new Error("modelSetkey is None or zero length");

    if (dispKey == null || dispKey.length == 0)
        throw new Error("dispKey is None or zero length");

    let hash = 0;

    for (let i = 0; i < dispKey.length; i++) {
        hash = (hash << 5) - hash + dispKey.charCodeAt(i);
        hash |= 0; // Convert to 32bit integer
    }

    hash = hash & (BUCKET_COUNT - 1); // 1024 buckets

    return `${modelSetKey}:${hash}`;
}

// ----------------------------------------------------------------------------
/** PrivateDiagramLocationLoaderService Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage of the index
 *
 * 2) Return DispKey locations based on the index.
 *
 */
@Injectable()
export class PrivateDiagramLocationLoaderService extends NgLifeCycleEvents {
    private UPDATE_CHUNK_FETCH_SIZE = 5;

    // Every 100 chunks from the server
    private SAVE_POINT_ITERATIONS = 100;

    // Saving the cache after each chunk is so expensive, we only do it every 20 or so
    private chunksSavedSinceLastIndexSave = 0;

    private index: LocationIndexUpdateDateTuple | null = null;
    private askServerChunks: LocationIndexUpdateDateTuple[] = [];

    private _hasLoaded$ = new BehaviorSubject<boolean>(false);

    private storage: TupleOfflineStorageService;

    private _statusSubject = new Subject<OfflineCacheLoaderStatusTuple>();
    private _status = new OfflineCacheLoaderStatusTuple();

    private coordSetService: PrivateDiagramCoordSetService;

    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        storageFactory: TupleStorageFactoryService,
        abstractCoordSetService: DiagramCoordSetService,
        private tupleService: PrivateDiagramTupleService,
        private deviceCacheControllerService: DeviceOfflineCacheService,
    ) {
        super();

        this._status.pluginName = "peek_plugin_diagram";
        this._status.indexName = "Position";

        this.coordSetService = <PrivateDiagramCoordSetService>(
            abstractCoordSetService
        );

        this.storage = new TupleOfflineStorageService(
            storageFactory,
            new TupleOfflineStorageNameService(locationIndexCacheStorageName),
        );

        this.setupVortexSubscriptions();

        this.deviceCacheControllerService.offlineModeEnabled$
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((v) => v))
            .pipe(first())
            .subscribe(() => {
                this.initialLoad();
            });

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

    private get _hasLoaded(): boolean {
        return this._hasLoaded$.getValue();
    }

    private set _hasLoaded(value: boolean) {
        this._hasLoaded$.next(value);
    }

    isReady(): boolean {
        return this._hasLoaded;
    }

    isReadyObservable(): Observable<boolean> {
        return this._hasLoaded$;
    }

    statusObservable(): Observable<OfflineCacheLoaderStatusTuple> {
        return this._statusSubject;
    }

    status(): OfflineCacheLoaderStatusTuple {
        return this._status;
    }

    /** Get Locations
     *
     * Get the location of a Disp.key from the index..
     *
     */

    /** Get Locations
     *
     * Get the location of a Disp.key from the index..
     *
     */
    async getLocations(
        modelSetKey: string,
        dispKey: string,
    ): Promise<DispKeyLocationTuple[]> {
        if (
            dispKey == null ||
            dispKey.length == 0 ||
            modelSetKey == null ||
            modelSetKey.length == 0
        ) {
            return [];
        }

        // If there is no offline support, or we're online
        if (this.vortexStatusService.snapshot.isOnline) {
            const ts = new TupleSelector(DispKeyLocationTuple.tupleName, {
                modelSetKey: modelSetKey,
                keys: [dispKey],
            });

            if (!this.vortexStatusService.snapshot.isOnline) {
                await firstValueFrom(
                    this.vortexStatusService.isOnline.pipe(
                        filter((online) => online),
                        first(),
                    ),
                );
            }

            return <DispKeyLocationTuple[]>(
                await this.tupleService.offlineObserver.pollForTuples(ts, false)
            );
        }

        if (!this.deviceCacheControllerService.offlineModeEnabled) {
            console.log(
                "WARNING Offline support for Diagram is disabled," +
                    " returning zero results",
            );
            return [];
        }

        // If we do have offline support
        if (this.isReady()) {
            return await this.getLocationsFromLocal(modelSetKey, dispKey);
        }

        await firstValueFrom(
            this.isReadyObservable().pipe(filter((ready) => ready)),
        );

        return await this.getLocationsFromLocal(modelSetKey, dispKey);
    }

    private _notifyStatus(paused: boolean = false): void {
        this._status.lastCheckDate = new Date();
        this._status.paused = paused;
        this._status.initialFullLoadComplete = this.index.initialLoadComplete;

        this._status.loadingQueueCount = 0;
        for (let chunk of this.askServerChunks) {
            this._status.loadingQueueCount += Object.keys(
                chunk.updateDateByChunkKey,
            ).length;
        }

        this._statusSubject.next(this._status);
        this.deviceCacheControllerService.updateLoaderCachingStatus(
            this._status,
        );
    }

    /** Initial load
     *
     * Load the dates of the index buckets and ask the server if it has any updates.
     */
    private initialLoad(): void {
        this.storage
            .loadTuples(new UpdateDateTupleSelector())
            .then((tuplesAny: any[]) => {
                let tuples: LocationIndexUpdateDateTuple[] = tuplesAny;
                if (tuples.length === 0) {
                    this.index = new LocationIndexUpdateDateTuple();
                } else {
                    this.index = tuples[0];

                    if (this.index.initialLoadComplete) {
                        this._hasLoaded = true;
                    }
                }

                this._notifyStatus();
            });
    }

    private setupVortexSubscriptions(): void {
        // Services don't have destructors, I'm not sure how to unsubscribe.
        this.vortexService
            .createEndpointObservable(
                this,
                clientLocationIndexWatchUpdateFromDeviceFilt,
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((payloadEnvelope: PayloadEnvelope) => {
                this.processChunksFromServer(payloadEnvelope);
            });
    }

    private areWeTalkingToTheServer(): boolean {
        return (
            this.deviceCacheControllerService.offlineModeEnabled &&
            this.vortexStatusService.snapshot.isOnline
        );
    }

    /** Ask Server For Updates
     *
     * Tell the server the state of the chunks in our index and ask if there
     * are updates.
     *
     */
    private askServerForUpdates() {
        if (!this.areWeTalkingToTheServer()) return;

        // If we're still caching, then exit
        if (this.askServerChunks.length != 0) {
            this.askServerForNextUpdateChunk();
            return;
        }

        this.tupleService.observer
            .pollForTuples(new UpdateDateTupleSelector())
            .then((tuplesAny: any) => {
                let serverIndex: LocationIndexUpdateDateTuple = tuplesAny[0];
                let keys = Object.keys(serverIndex.updateDateByChunkKey);
                let keysNeedingUpdate: string[] = [];

                this._status.totalLoadedCount = keys.length;

                // Tuples is an array of strings
                for (let chunkKey of keys) {
                    if (
                        !this.index.updateDateByChunkKey.hasOwnProperty(
                            chunkKey,
                        )
                    ) {
                        this.index.updateDateByChunkKey[chunkKey] = null;
                        keysNeedingUpdate.push(chunkKey);
                    } else if (
                        this.index.updateDateByChunkKey[chunkKey] !=
                        serverIndex.updateDateByChunkKey[chunkKey]
                    ) {
                        keysNeedingUpdate.push(chunkKey);
                    }
                }

                if (
                    keysNeedingUpdate.length === 0 &&
                    !this.index.initialLoadComplete
                )
                    this.index.initialLoadComplete = true;

                this.queueChunksToAskServer(keysNeedingUpdate);
            });
    }

    /** Queue Chunks To Ask Server
     *
     */
    private queueChunksToAskServer(keysNeedingUpdate: string[]) {
        if (!this.areWeTalkingToTheServer()) return;

        this.askServerChunks = [];

        let count = 0;
        let indexChunk = new LocationIndexUpdateDateTuple();

        for (let key of keysNeedingUpdate) {
            indexChunk.updateDateByChunkKey[key] =
                this.index.updateDateByChunkKey[key] || "";
            count++;

            if (count == this.UPDATE_CHUNK_FETCH_SIZE) {
                this.askServerChunks.push(indexChunk);
                count = 0;
                indexChunk = new LocationIndexUpdateDateTuple();
            }
        }

        if (count) this.askServerChunks.push(indexChunk);

        this.askServerForNextUpdateChunk();

        this._status.lastCheckDate = new Date();
        this._notifyStatus();
    }

    private askServerForNextUpdateChunk() {
        if (!this.areWeTalkingToTheServer()) return;

        if (this.askServerChunks.length == 0) return;

        if (this.deviceCacheControllerService.isOfflineCachingPaused) {
            this.saveChunkCacheIndex(true) //
                .catch((e) => console.log(`ERROR saveChunkCacheIndex: ${e}`));
            this._notifyStatus(true);
            return;
        }

        let indexChunk: LocationIndexUpdateDateTuple =
            this.askServerChunks.pop();

        let filt = Object.assign(
            {},
            clientLocationIndexWatchUpdateFromDeviceFilt,
        );
        filt[cacheAll] = true;
        let payload = new Payload(filt, [indexChunk]);
        this.vortexService.sendPayload(payload);

        this._status.lastCheckDate = new Date();
        this._notifyStatus();
    }

    /** Process LocationIndexes From Server
     *
     * Process the grids the server has sent us.
     */
    private async processChunksFromServer(
        payloadEnvelope: PayloadEnvelope,
    ): Promise<void> {
        if (payloadEnvelope.result != null && payloadEnvelope.result != true) {
            console.log(`ERROR: ${payloadEnvelope.result}`);
            return;
        }

        const tuplesToSave: EncodedLocationIndexTuple[] = <
            EncodedLocationIndexTuple[]
        >payloadEnvelope.data;

        try {
            await this.storeChunkTuples(tuplesToSave);
        } catch (e) {
            console.log(`LocationIndexCache.storeChunkTuples: ${e}`);
        }

        if (this.askServerChunks.length == 0) {
            this.index.initialLoadComplete = true;
            await this.saveChunkCacheIndex(true);
            this._hasLoaded = true;
        } else if (payloadEnvelope.filt[cacheAll] == true) {
            this.askServerForNextUpdateChunk();
        }

        this._notifyStatus();
    }

    /** Store Index Bucket
     * Stores the index bucket in the local db.
     */
    private async storeChunkTuples(
        tuplesToSave: EncodedLocationIndexTuple[],
    ): Promise<void> {
        // noinspection BadExpressionStatementJS
        const Selector = LocationIndexTupleSelector;

        if (tuplesToSave.length == 0) return;

        const batchStore: TupleStorageBatchSaveArguments[] = [];
        for (const tuple of tuplesToSave) {
            batchStore.push({
                tupleSelector: new Selector(tuple.chunkKey),
                vortexMsg: tuple.encodedData,
            });
        }

        await this.storage.batchSaveTuplesEncoded(batchStore);

        for (const tuple of tuplesToSave) {
            this.index.updateDateByChunkKey[tuple.chunkKey] = tuple.lastUpdate;
        }
        await this.saveChunkCacheIndex();
    }

    /** Store Chunk Cache Index
     *
     * Updates our running tab of the update dates of the cached chunks
     *
     */
    private async saveChunkCacheIndex(force = false): Promise<void> {
        if (
            this.chunksSavedSinceLastIndexSave <= this.SAVE_POINT_ITERATIONS &&
            !force
        ) {
            return;
        }

        this.chunksSavedSinceLastIndexSave = 0;

        await this.storage.saveTuples(new UpdateDateTupleSelector(), [
            this.index,
        ]);
    }

    /** Get Locations
     *
     * Get the location of a Disp.key from the index..
     *
     */
    private getLocationsFromLocal(
        modelSetKey: string,
        dispKey: string,
    ): Promise<DispKeyLocationTuple[]> {
        let indexBucket = dispKeyHashBucket(modelSetKey, dispKey);

        if (!this.index.updateDateByChunkKey.hasOwnProperty(indexBucket)) {
            console.log(`DispKey ${dispKey} doesn't appear in the index`);
            return Promise.resolve([]);
        }

        let retPromise: any;
        retPromise = this.storage
            .loadTuples(new LocationIndexTupleSelector(indexBucket))
            .then((tuples: LocationIndexTuple[]) => {
                if (tuples.length == 0) return [];

                if (tuples.length != 1)
                    throw new Error("We received more tuples then expected");

                let dispIndexArray = JSON.parse(tuples[0].jsonStr);

                let dispLocationIndexRawData: any[] | null = null;

                // TODO These keys are sorted, so we can do a binary search.
                for (let i = 0; i < dispIndexArray.length; i++) {
                    if (dispIndexArray[i][0] == dispKey) {
                        dispLocationIndexRawData = dispIndexArray[i].slice(1);
                        break;
                    }
                }

                // If we didn't find the key, return no indexes
                if (dispLocationIndexRawData == null) return [];

                let dispIndexes: DispKeyLocationTuple[] = [];
                for (let rawData of dispLocationIndexRawData) {
                    let dispLocation =
                        DispKeyLocationTuple.fromLocationJson(rawData);

                    let coordSet = this.coordSetService.coordSetForId(
                        dispLocation.coordSetId,
                    );

                    if (coordSet == null) continue;

                    dispLocation.coordSetKey = coordSet.key;

                    dispIndexes.push(dispLocation);
                }

                return dispIndexes;
            });
        return retPromise;
    }
}
