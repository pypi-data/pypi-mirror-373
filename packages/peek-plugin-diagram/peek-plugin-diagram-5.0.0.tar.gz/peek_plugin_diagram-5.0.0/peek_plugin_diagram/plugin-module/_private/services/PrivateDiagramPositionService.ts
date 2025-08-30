import { Injectable } from "@angular/core";
import {
    CoordSetViewWindowI,
    DiagramPositionService,
    DispKeyLocation,
    OptionalPositionArgsI,
    PositionUpdatedI,
} from "../../DiagramPositionService";
import { BehaviorSubject, Observable, Subject } from "rxjs";

import { DispKeyLocationTuple } from "../location-loader/DispKeyLocationTuple";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { PrivateDiagramLocationLoaderService } from "../location-loader";
import { PrivateDiagramCoordSetService } from "./PrivateDiagramCoordSetService";

export interface DiagramPositionI {
    coordSetKey: string;
    x: number;
    y: number;
    zoom: number;
    opts: OptionalPositionArgsI;
}

export interface DiagramPositionByKeyI {
    modelSetKey: string;
    coordSetKey: string | null;
    opts: OptionalPositionArgsI;
    dispKeyIndexes: DispKeyLocationTuple[] | null;
}

export interface DiagramPositionByCoordSetI {
    modelSetKey: string | null;
    coordSetKey: string | null;
}

@Injectable()
export class PrivateDiagramPositionService extends DiagramPositionService {
    // This observable is for when the canvas updates the title
    private titleUpdatedSubject = new BehaviorSubject<string | null>(null);
    private positionByCoordSetSubject =
        new BehaviorSubject<null | DiagramPositionByCoordSetI>(null);
    private positionSubject = new BehaviorSubject<DiagramPositionI | null>(
        null,
    );
    private positionByKeySubject =
        new BehaviorSubject<DiagramPositionByKeyI | null>(null);
    private isReady$ = new BehaviorSubject<boolean>(false);

    private positionUpdatedSubject = new Subject<PositionUpdatedI>();
    private coordSetViewSubject =
        new BehaviorSubject<null | CoordSetViewWindowI>(null);

    private selectKeysSubject = new BehaviorSubject<string[] | null>(null);

    constructor(
        private coordSetService: PrivateDiagramCoordSetService,
        private locationIndexService: PrivateDiagramLocationLoaderService,
        private balloonMsg: BalloonMsgService,
    ) {
        super();
    }

    positionByCoordSet(modelSetKey: string, coordSetKey: string): void {
        this.positionByCoordSetSubject.next({ modelSetKey, coordSetKey });
    }

    position(
        coordSetKey: string,
        x: number,
        y: number,
        zoom: number,
        opts: OptionalPositionArgsI = {},
    ): void {
        this.positionSubject.next({
            coordSetKey: coordSetKey,
            x: x,
            y: y,
            zoom: zoom,
            opts,
        });
    }

    async positionByKeys(
        keys: string[],
        modelSetKey: string,
        coordSetKey: string,
    ): Promise<void> {
        const locations: any[] = [];

        for (const key of keys) {
            const keyLocations = await this.locationsForKey(modelSetKey, key);

            if (keyLocations?.length === 0) {
                continue;
            }

            const keyLocation = keyLocations[0].positions;

            locations.push(...keyLocation);
        }

        let x = 0;
        let y = 0;

        for (const location of locations) {
            x += location.x;
            y += location.y;
        }

        x /= locations.length;
        y /= locations.length;

        this.position(
            coordSetKey,
            parseFloat(x.toString()),
            parseFloat(y.toString()),
            parseFloat("0.85"),
            {},
        );

        this.selectKeysSubject.next(keys);
    }

    async positionByKey(
        modelSetKey: string,
        coordSetKey: string | null,
        opts: OptionalPositionArgsI | null = null,
    ): Promise<void> {
        if (!this.coordSetService.isReady()) {
            throw new Error(
                "positionByKey called before coordSetService is ready",
            );
        }
        opts = opts || {};

        if (opts.highlightKey == null || opts.highlightKey.length == 0)
            throw new Error("positionByKey must be passed opts.highlightKey");

        let dispKeyIndexes: DispKeyLocationTuple[] =
            await this.locationIndexService.getLocations(
                modelSetKey,
                opts.highlightKey,
            );

        // If a closestPoint has been provided, then filter for that

        if (opts.closestToPoint != null && coordSetKey != null) {
            const closestResults = dispKeyIndexes
                .filter((r) => r.coordSetKey == coordSetKey)
                .sort((a, b) => {
                    const distanceA = Math.sqrt(
                        Math.pow(a.x - opts.closestToPoint.x, 2) +
                            Math.pow(a.y - opts.closestToPoint.y, 2),
                    );
                    const distanceB = Math.sqrt(
                        Math.pow(b.x - opts.closestToPoint.x, 2) +
                            Math.pow(b.y - opts.closestToPoint.y, 2),
                    );
                    return distanceA - distanceB;
                });

            if (closestResults.length !== 0) {
                console.log(
                    `Selecting closest result to ` +
                        ` ${opts.closestToPoint.x}x${opts.closestToPoint.y}` +
                        ` in coordSet ${coordSetKey}`,
                );
                dispKeyIndexes = [closestResults[0]];
            }
        }

        if (dispKeyIndexes.length == 0) {
            this.balloonMsg.showError(
                `Can not locate display item ${opts.highlightKey}` +
                    ` in model set ${modelSetKey}`,
            );
        }

        if (coordSetKey != null) {
            dispKeyIndexes = dispKeyIndexes //
                .filter((d) => d.coordSetKey === coordSetKey);

            if (!dispKeyIndexes.length) {
                this.balloonMsg.showError(
                    `Can not locate display item ${opts.highlightKey}` +
                        ` in model set ${modelSetKey}, in coord set ${coordSetKey}`,
                );
            }
        }

        if (dispKeyIndexes.length === 1) {
            const dispKeyIndex = dispKeyIndexes[0];

            const coordSet = this.coordSetService.coordSetForKey(
                modelSetKey,
                dispKeyIndex.coordSetKey,
            );

            if (coordSet == null) {
                throw new Error(
                    "Could not find coordSet for key=" +
                        dispKeyIndex.coordSetKey,
                );
            }

            this.positionSubject.next({
                coordSetKey: dispKeyIndex.coordSetKey,
                x: dispKeyIndex.x,
                y: dispKeyIndex.y,
                zoom: coordSet.positionOnZoom,
                opts,
            });

            return;
        }

        // Emitting this will cause the diagram to ask the user what to do.
        this.positionByKeySubject.next({
            modelSetKey: modelSetKey,
            coordSetKey: coordSetKey,
            opts: opts,
            dispKeyIndexes: dispKeyIndexes,
        });
    }

    async canPositionByKey(
        modelSetKey: string,
        dispKey: string,
    ): Promise<boolean> {
        const val: DispKeyLocationTuple[] =
            await this.locationIndexService.getLocations(modelSetKey, dispKey);
        return val.length != 0;
    }

    async locationsForKey(
        modelSetKey: string,
        dispKey: string,
    ): Promise<DispKeyLocation[]> {
        const tuples: DispKeyLocationTuple[] =
            await this.locationIndexService.getLocations(modelSetKey, dispKey);

        const locations: DispKeyLocation[] = [];
        const locationByCoordSet: { [coordSetKey: string]: DispKeyLocation } =
            {};
        for (const tuple of tuples) {
            let location = locationByCoordSet[tuple.coordSetKey];
            if (location == null) {
                location = {
                    modelSetKey: modelSetKey,
                    coordSetKey: tuple.coordSetKey,
                    dispKey: dispKey,
                    positions: [],
                    zoom: 2.0,
                };
                locationByCoordSet[tuple.coordSetKey] = location;
                locations.push(location);
            }

            location.positions.push({ x: tuple.x, y: tuple.y });
        }
        return locations;
    }

    setReady() {
        this.isReady$.next(true);
    }

    setTitle(value: string) {
        this.titleUpdatedSubject.next(value);
    }

    positionUpdated(
        pos: PositionUpdatedI,
        coordSetViewData: CoordSetViewWindowI,
    ): void {
        this.positionUpdatedSubject.next(pos);
        this.coordSetViewSubject.next(coordSetViewData);
    }

    isReadyObservable(): Observable<boolean> {
        return this.isReady$.asObservable();
    }

    positionUpdatedObservable(): Observable<PositionUpdatedI> {
        return this.positionUpdatedSubject;
    }

    coordSetViewUpdatedObservable(): Observable<CoordSetViewWindowI | null> {
        return this.coordSetViewSubject.asObservable();
    }

    coordSetView(): CoordSetViewWindowI | null {
        return this.coordSetViewSubject.getValue();
    }

    titleUpdatedObservable(): Observable<string | null> {
        return this.titleUpdatedSubject.asObservable();
    }

    // The following methods are used in the set-position.component.ts
    // in setupSubscriptions

    positionObservable(): Observable<DiagramPositionI | null> {
        return this.positionSubject.asObservable();
    }

    clearPositionObservable(): void {
        this.positionSubject.next(null);
    }

    positionByKeyObservable(): Observable<DiagramPositionByKeyI | null> {
        return this.positionByKeySubject.asObservable();
    }

    clearPositionByKeyObservable(): void {
        this.positionByKeySubject.next(null);
    }

    positionByCoordSetObservable(): Observable<DiagramPositionByCoordSetI | null> {
        return this.positionByCoordSetSubject.asObservable();
    }

    clearPositionByCoordSetObservable(): void {
        this.positionByCoordSetSubject.next(null);
    }

    selectKeysObservable(): Observable<string[] | null> {
        return this.selectKeysSubject.asObservable();
    }

    clearSelectKeysObservable(): void {
        this.selectKeysSubject.next(null);
    }
}
