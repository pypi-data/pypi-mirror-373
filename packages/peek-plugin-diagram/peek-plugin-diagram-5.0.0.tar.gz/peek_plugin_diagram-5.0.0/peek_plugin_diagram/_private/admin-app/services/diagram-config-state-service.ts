import { Injectable } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BehaviorSubject, Observable } from "rxjs";
import { map } from "rxjs/operators";
import { ConfigColorLookupListTuple } from "../tuples/config-color-lookup-list-tuple";
import { ConfigLayerLookupListTuple } from "../tuples/config-layer-lookup-list-tuple";
import { ConfigLevelLookupListTuple } from "../tuples/config-level-lookup-list-tuple";
import { ConfigTextStyleLookupListTuple } from "../tuples/config-text-style-lookup-list-tuple";
import { ConfigLineStyleLookupListTuple } from "../tuples/config-line-style-lookup-list-tuple";

export enum ConfigObjectTypeE {
    ModelSet = 1,
    Canvas,
    ColorLookup,
    LevelLookup,
    LayerLookup,
    TextStyleLookup,
    LineStyleLookup,
}

export function isLookupType(type: ConfigObjectTypeE): boolean {
    return (
        type === ConfigObjectTypeE.ColorLookup ||
        type === ConfigObjectTypeE.LayerLookup ||
        type === ConfigObjectTypeE.LevelLookup ||
        type === ConfigObjectTypeE.TextStyleLookup ||
        type === ConfigObjectTypeE.LineStyleLookup
    );
}

export type LookupTypeT =
    | ConfigObjectTypeE.LevelLookup
    | ConfigObjectTypeE.ColorLookup
    | ConfigObjectTypeE.LayerLookup
    | ConfigObjectTypeE.LineStyleLookup
    | ConfigObjectTypeE.TextStyleLookup;

export type LookupListTupleType =
    | ConfigColorLookupListTuple
    | ConfigLayerLookupListTuple
    | ConfigLevelLookupListTuple
    | ConfigTextStyleLookupListTuple
    | ConfigLineStyleLookupListTuple;

export interface CreatedLookupResultI {
    id: number;
    importHash: string;
}

export interface NewLookupWithModelSetI {
    modelSetId: number;
    name: string;
    importHash: string;
    result: CreatedLookupResultI | null;
}

export interface NewLookupWithCoordSetI {
    coordSetId: number;
    name: string;
    importHash: string;
    result: CreatedLookupResultI | null;
}

@Injectable({
    providedIn: "root",
})
export class DiagramConfigStateService extends NgLifeCycleEvents {
    private readonly _selectedConfigList$ = new BehaviorSubject<
        [ConfigObjectTypeE, number] | null
    >(null);

    private readonly _selectedConfigObject$ = new BehaviorSubject<
        [ConfigObjectTypeE, number] | null
    >(null);

    constructor() {
        super();
    }

    resetConfigList() {
        this._selectedConfigList$.next(null);
    }

    selectConfigList(objectType: ConfigObjectTypeE, parentId: number) {
        this._selectedConfigList$.next([objectType, parentId]);
    }

    resetConfigObject() {
        this._selectedConfigObject$.next(null);
    }

    selectConfigObject(objectType: ConfigObjectTypeE, objectId: number) {
        this._selectedConfigObject$.next([objectType, objectId]);
    }

    get modelConfigSelected$(): Observable<number | null> {
        return this._selectedConfigObject$.pipe(
            map((value) => {
                if (value == null) {
                    return null;
                }
                const [objectType, objectId] = value;
                return objectType === ConfigObjectTypeE.ModelSet
                    ? objectId
                    : null;
            }),
        );
    }

    get canvasConfigSelected$(): Observable<number | null> {
        return this._selectedConfigObject$.pipe(
            map((value) => {
                if (value == null) {
                    return null;
                }
                const [objectType, objectId] = value;
                return objectType === ConfigObjectTypeE.Canvas
                    ? objectId
                    : null;
            }),
        );
    }

    private lookupMapArrowFunction(
        value: [ConfigObjectTypeE, number] | null,
    ): [LookupTypeT, number] | null {
        if (value == null) {
            return null;
        }
        const [objectType, objectId] = value;
        if (isLookupType(objectType)) {
            return [objectType as LookupTypeT, objectId];
        }

        return null;
    }

    get lookupListConfigSelected$(): Observable<[LookupTypeT, number] | null> {
        return this._selectedConfigList$.pipe(
            map((v) => this.lookupMapArrowFunction(v)),
        );
    }

    get lookupItemConfigSelected$(): Observable<[LookupTypeT, number] | null> {
        return this._selectedConfigObject$.pipe(
            map((v) => this.lookupMapArrowFunction(v)),
        );
    }
}
