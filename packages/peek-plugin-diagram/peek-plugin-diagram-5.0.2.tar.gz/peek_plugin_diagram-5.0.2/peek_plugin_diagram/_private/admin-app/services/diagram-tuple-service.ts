import { Injectable } from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataLoader,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import {
    diagramActionProcessorName,
    diagramFilt,
    diagramObservableName,
    diagramTupleOfflineServiceName,
} from "@peek/peek_plugin_diagram/_private";
import { BehaviorSubject, firstValueFrom } from "rxjs";
import { ConfigModelSetListTuple } from "../tuples/config-model-list-tuple";
import { ConfigCanvasListTuple } from "../tuples/config-canvas-list-tuple";
import { map } from "rxjs/operators";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        diagramActionProcessorName,
        diagramFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        diagramObservableName,
        diagramFilt,
    );
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(diagramTupleOfflineServiceName);
}

@Injectable({
    providedIn: "root",
})
export class DiagramTupleService extends NgLifeCycleEvents {
    public readonly observer: TupleDataObserverService;
    public readonly action: TupleActionPushService;
    public readonly offlineObserver: TupleDataOfflineObserverService;
    public readonly offlineStorage: TupleOfflineStorageService;
    public readonly dataLoader: TupleDataLoader;
    public readonly userUuid$ = new BehaviorSubject<string>("");

    constructor(
        storageFactory: TupleStorageFactoryService,
        vortexService: VortexService,
        vortexStatusService: VortexStatusService,
    ) {
        super();

        this.offlineStorage = new TupleOfflineStorageService(
            storageFactory,
            tupleOfflineStorageNameServiceFactory(),
        );

        // Online Actions
        this.action = new TupleActionPushService(
            tupleActionPushNameServiceFactory(),
            vortexService,
            vortexStatusService,
        );

        // Register the observer
        let observerName = tupleDataObservableNameServiceFactory();
        this.offlineObserver = new TupleDataOfflineObserverService(
            vortexService,
            vortexStatusService,
            observerName,
            this.offlineStorage,
        );
        this.observer = new TupleDataObserverService(
            this.offlineObserver,
            observerName,
        );

        this.dataLoader = new TupleDataLoader(this, this.action, this.observer);
    }

    async getModelSet(modelSetKey: string) {
        const modelSets = await firstValueFrom(
            this.observer
                .subscribeToTupleSelector(
                    new TupleSelector(ConfigModelSetListTuple.tupleName, {}),
                )
                .pipe(
                    map(
                        (tuples: Tuple[]) =>
                            tuples as ConfigModelSetListTuple[],
                    ),
                ),
        );

        const modelSet = modelSets.find((ms) => ms.key == modelSetKey);

        if (modelSet == null) {
            throw new Error(`ModelSet ${modelSetKey} not found`);
        }
        return modelSet;
    }

    async getCoordSet(modelSetId: number, coordSetKey: string) {
        const coordSets = (await firstValueFrom(
            this.observer.subscribeToTupleSelector(
                new TupleSelector(ConfigCanvasListTuple.tupleName, {
                    modelSetId: modelSetId,
                }),
            ),
        )) as ConfigCanvasListTuple[];

        const coordSet = coordSets.find((item) => item.key == coordSetKey);

        if (coordSet == null) {
            throw new Error(
                `CoordSet  with modelSetId=${modelSetId}` +
                    ` key=${coordSetKey} not found`,
            );
        }
        return coordSet;
    }
}
