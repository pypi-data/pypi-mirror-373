import { BehaviorSubject, Observable, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import {
    DispColor,
    DispLayer,
    DispLevel,
    DispLineStyle,
    DispTextStyle,
} from "../lookups";
import { PrivateDiagramTupleService } from "./PrivateDiagramTupleService";
import { ModelSet } from "../tuples";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";

let dictValuesFromObject = (dict) => Object.keys(dict).map((key) => dict[key]);

/** Lookup Cache
 *
 * This class provides handy access to the lookup objects
 *
 * Typically there will be only a few hundred of these.
 *
 */
@Injectable()
export class PrivateDiagramLookupService extends NgLifeCycleEvents {
    private loadedCounter = {};
    private _lookupTargetCount = 6;
    private _levelsById = {};
    private _layersById = {};
    private _colorsByModelSetIdByName: {
        [id: number]: { [name: string]: DispColor };
    } = {};
    private _colorById: { [id: number]: DispColor } = {};
    private _textStyleById = {};
    private _lineStyleById = {};
    private _levelsByCoordSetIdOrderedByOrder: { [id: number]: DispLevel[] } =
        {};
    private _layersByModelSetIdOrderedByOrder: { [id: number]: DispLayer[] } =
        {};
    private _colorsByModelSetIdOrderedByName: { [id: number]: DispColor[] } =
        {};
    private _textStyleByModelSetIdOrderedByName: {
        [id: number]: DispTextStyle[];
    } = {};
    private _lineStyleByModelSetIdOrderedByName: {
        [id: number]: DispLineStyle[];
    } = {};
    private unsub = new Subject<void>();

    private _hasLoaded$ = new BehaviorSubject<boolean>(false);
    private modelSetByKey: { [key: string]: ModelSet } = {};
    private dispsNeedRelinkingSubject = new Subject<void>();
    private dispsNeedRelinking = false;

    constructor(
        private tupleService: PrivateDiagramTupleService,
        private coordSetService: PrivateDiagramCoordSetService,
    ) {
        super();

        const modelSetTs = new TupleSelector(ModelSet.tupleName, {});
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(modelSetTs)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((modelSets: ModelSet[]) => {
                this.modelSetByKey = {};
                for (let modelSet of modelSets)
                    this.modelSetByKey[modelSet.key] = modelSet;

                this.loadedCounter["modelSet"] = true;

                this._hasLoaded$.next(this.isReady());
                this.dispsNeedRelinking = true;
            });

        const sub = (
            lookupAttr,
            tupleName,
            callback = null,
            indexAttrName = "id",
        ) => {
            this.tupleService.offlineObserver
                .subscribeToTupleSelector(new TupleSelector(tupleName, {}))
                .pipe(takeUntil(this.unsub))
                .subscribe((tuples: any[]) => {
                    if (!tuples.length) return;

                    this.loadedCounter[lookupAttr] = true;
                    this[lookupAttr] = {};

                    for (const item of tuples) {
                        this[lookupAttr][item[indexAttrName]] = item;
                    }

                    if (callback != null) {
                        callback();
                    }

                    this._hasLoaded$.next(this.isReady());
                    this.dispsNeedRelinking = true;
                });
        };

        // Load the lookup after the model set loads
        sub("_levelsById", DispLevel.tupleName, () =>
            this.createLevelsOrderedByOrder(),
        );

        sub("_layersById", DispLayer.tupleName, () => {
            this.createLayersOrderedByOrder();
            this.populateLayerRelationships();
            this.initialiseLayerDefaults();
        });

        sub("_colorById", DispColor.tupleName, () => {
            this._validateColors();
            this.loadColorImageFromBase64();
            this.createColorByNameByModelSetKey();
        });

        sub("_textStyleById", DispTextStyle.tupleName, () =>
            this.createTextStyleOrderedByName(),
        );

        sub("_lineStyleById", DispLineStyle.tupleName, () =>
            this._convertLineStyleDashPattern(),
        );

        setInterval(() => {
            if (!this.dispsNeedRelinking) return;
            this.dispsNeedRelinkingSubject.next();
            this.dispsNeedRelinking = false;
        }, 500);
    }

    private get _hasLoaded(): boolean {
        return this._hasLoaded$.getValue();
    }

    private set _hasLoaded(value: boolean) {
        this._hasLoaded$.next(value);
    }

    isReady(): boolean {
        // isReady is used in a doCheck loop, so make if fast once it's true
        if (this._hasLoaded) return true;

        let loadedCount = Object.keys(this.loadedCounter).length;
        if (this._lookupTargetCount != loadedCount) return false;

        this._hasLoaded = true;
        return true;
    }

    isReadyObservable(): Observable<boolean> {
        return this._hasLoaded$;
    }

    updateCanvasPatterns(ctx: CanvasRenderingContext2D): void {
        const colors: DispColor[] = dictValuesFromObject(this._colorById);

        for (const color of colors) {
            color._darkFillCanvasPattern = null;
            color._lightFillCanvasPattern = null;

            if (color._darkFillImage) {
                color._darkFillCanvasPattern = ctx.createPattern(
                    color._darkFillImage,
                    "repeat",
                );
            }

            if (color._lightFillImage) {
                color._lightFillCanvasPattern = ctx.createPattern(
                    color._lightFillImage,
                    "repeat",
                );
            }
        }
    }

    /** Disps Need Relinking Observable
     *
     * The returned observable fires when new lookups have been loaded from the server.
     * This will require the disps in the cache to relink.
     *
     */
    dispsNeedRelinkingObservable(): Observable<void> {
        return this.dispsNeedRelinkingSubject;
    }

    shutdown() {
        this.unsub.next();
    }

    // ============================================================================
    // Load Callbacks

    levelForId(levelId: number): DispLevel {
        return this._levelsById[levelId];
    }

    layerForName(modelSetKey: string, layerName: string): DispLayer | null {
        for (let layer of this.layersOrderedByOrder(modelSetKey)) {
            if (layer.name == layerName) return layer;
        }
        return null;
    }

    layerForId(layerId: number): DispLayer {
        return this._layersById[layerId];
    }

    colorForName(
        modelSetKeyOrId: string | number,
        name: string,
    ): DispColor | null {
        const modelSetId = this.getModelSetId(modelSetKeyOrId);
        const result = this._colorsByModelSetIdByName[modelSetId];
        return result == null ? null : result[name.toLowerCase()];
    }

    colorForId(colorId: number): DispColor {
        return this._colorById[colorId];
    }

    textStyleForId(textStyleId: number): DispTextStyle {
        return this._textStyleById[textStyleId];
    }

    lineStyleForId(lineStyleId: number): DispLineStyle {
        return this._lineStyleById[lineStyleId];
    }

    layersOrderedByOrder(modelSetKeyOrId: number | string): DispLayer[] {
        let modelSetId = this.getModelSetId(modelSetKeyOrId);
        let result = this._layersByModelSetIdOrderedByOrder[modelSetId];
        return result == null ? [] : result.slice();
    }

    // ============================================================================
    // Accessors

    levelsOrderedByOrder(coordSetId: number): DispLevel[] {
        let result = this._levelsByCoordSetIdOrderedByOrder[coordSetId];
        return result == null ? [] : result.slice();
    }

    colorsOrderedByName(modelSetKeyOrId: number | string): DispColor[] {
        let modelSetId = this.getModelSetId(modelSetKeyOrId);
        let result = this._colorsByModelSetIdOrderedByName[modelSetId];
        return result == null ? [] : result.slice();
    }

    textStylesOrderedByName(modelSetKeyOrId: number | string): DispTextStyle[] {
        let modelSetId = this.getModelSetId(modelSetKeyOrId);
        let result = this._textStyleByModelSetIdOrderedByName[modelSetId];
        return result == null ? [] : result.slice();
    }

    lineStylesOrderedByName(modelSetKeyOrId: number | string): DispLineStyle[] {
        let modelSetId = this.getModelSetId(modelSetKeyOrId);
        let result = this._lineStyleByModelSetIdOrderedByName[modelSetId];
        return result == null ? [] : result.slice();
    }

    _linkDispLookups(disp) {
        if (disp.le != null) {
            disp.lel = this._levelsById[disp.le];
            if (disp.lel == null) return null;
        }

        if (disp.la != null) {
            disp.lal = this._layersById[disp.la];
            if (disp.lal == null) return null;
        }

        if (disp.fs != null) {
            disp.fsl = this._textStyleById[disp.fs];
            if (disp.fsl == null) return null;
        }

        if (disp.c != null) {
            disp.cl = this._colorById[disp.c];
            if (disp.cl == null) return null;
        }

        if (disp.bc != null) {
            disp.bcl = this._colorById[disp.bc];
            if (disp.bcl == null) return null;
        }

        if (disp.lc != null) {
            disp.lcl = this._colorById[disp.lc];
            if (disp.lcl == null) return null;
        }

        if (disp.ec != null) {
            disp.ecl = this._colorById[disp.ec];
            if (disp.ecl == null) return null;
        }

        if (disp.fc != null) {
            disp.fcl = this._colorById[disp.fc];
            if (disp.fcl == null) return null;
        }

        if (disp.ls != null) {
            disp.lsl = this._lineStyleById[disp.ls];
            if (disp.lsl == null) return null;
        }

        return disp;
    }

    private _validateColors() {
        function validTextColor(stringToTest) {
            // Nulls are allowed
            if ((stringToTest?.length || 0) === 0) {
                return true;
            }

            let image = document.createElement("img");
            image.style.color = "rgb(0, 0, 0)";
            image.style.color = stringToTest;
            if (image.style.color !== "rgb(0, 0, 0)") {
                return true;
            }
            image.style.color = "rgb(255, 255, 255)";
            image.style.color = stringToTest;
            return image.style.color !== "rgb(255, 255, 255)";
        }

        let colors = dictValuesFromObject(this._colorById);
        for (let i = 0; i < colors.length; i++) {
            let color: DispColor = colors[i];

            if ((color.darkColor?.length || 0) === 0) {
                color.darkColor = null;
            } else if (!validTextColor(color.darkColor)) {
                console.log(
                    `Color ID ${color.id} Dark Colour ${color.darkColor} is not a valid CSS color`,
                );
                color.darkColor = "red";
            }

            if ((color.lightColor?.length || 0) === 0) {
                color.lightColor = null;
            } else if (!validTextColor(color.lightColor)) {
                console.log(
                    `Color ID ${color.id} Light Colour` +
                        ` ${color.lightColor} is not a valid CSS color`,
                );
                color.lightColor = "red";
            }
        }

        let ordered = dictValuesFromObject(this._colorById).sort((o1, o2) =>
            o1.name.localeCompare(o2.name),
        );

        this._colorsByModelSetIdOrderedByName = this.groupByCommonId(
            ordered,
            "modelSetId",
        );
    }

    private loadColorImageFromBase64() {
        const colors: DispColor[] = dictValuesFromObject(this._colorById);

        for (const color of colors) {
            color._darkFillImage = null;
            color._lightFillImage = null;

            if (color.darkFillBase64Image) {
                color._darkFillImage = new Image();
                color._darkFillImage.src = color.darkFillBase64Image;
            }

            if (color.lightFillBase64Image) {
                color._lightFillImage = new Image();
                color._lightFillImage.src = color.lightFillBase64Image;
            }
        }
    }

    /** Convert Line Style Dash Pattern
     *
     * This method converts the line style json into an array of numbers
     */
    private _convertLineStyleDashPattern() {
        let lineStyles: DispLineStyle[] = dictValuesFromObject(
            this._lineStyleById,
        );

        for (let lineStyle of lineStyles) {
            if (lineStyle.dashPattern == null) continue;

            try {
                lineStyle.dashPatternParsed = JSON.parse(
                    "" + lineStyle.dashPattern,
                );
            } catch (e) {
                console.log(
                    `Warning: Can't parse` +
                        ` Dash Pattern: '${lineStyle.dashPattern}'` +
                        ` for lineStyle.id=${lineStyle.id}` +
                        ` error: ${e}`,
                );
                lineStyle.dashPatternParsed = [];
            }
        }

        let ordered = lineStyles.sort((o1, o2) =>
            o1.name.localeCompare(o2.name),
        );

        this._lineStyleByModelSetIdOrderedByName = this.groupByCommonId(
            ordered,
            "modelSetId",
        );
    }

    private createColorByNameByModelSetKey() {
        this._colorsByModelSetIdByName = {};

        for (const color of Object.values(this._colorById)) {
            let dict = this._colorsByModelSetIdByName[color.modelSetId];

            if (dict == null) {
                dict = {};
                this._colorsByModelSetIdByName[color.modelSetId] = dict;
            }

            dict[color.name.toLowerCase()] = color;
        }
    }

    private createLayersOrderedByOrder() {
        let ordered = dictValuesFromObject(this._layersById).sort(
            (o1, o2) => o1.order - o2.order,
        );

        this._layersByModelSetIdOrderedByOrder = this.groupByCommonId(
            ordered,
            "modelSetId",
        );
    }

    private populateLayerRelationships() {
        const layers: DispLayer[] = dictValuesFromObject(this._layersById);

        // Clear existing relationships
        for (const layer of layers) {
            layer.parentLayer = null;
            layer.childLayers = [];
        }

        // Establish parent-child relationships
        for (const layer of layers) {
            if (layer.parentId != null) {
                const parentLayer = this._layersById[layer.parentId];
                if (parentLayer) {
                    layer.parentLayer = parentLayer;
                    parentLayer.childLayers.push(layer);
                }
            }
        }
    }

    private createLevelsOrderedByOrder() {
        let ordered = dictValuesFromObject(this._levelsById).sort(
            (o1, o2) => o1.order - o2.order,
        );

        this._levelsByCoordSetIdOrderedByOrder = this.groupByCommonId(
            ordered,
            "coordSetId",
        );
    }

    private createTextStyleOrderedByName() {
        let ordered = dictValuesFromObject(this._textStyleById).sort((o1, o2) =>
            o1.name.localeCompare(o2.name),
        );

        this._textStyleByModelSetIdOrderedByName = this.groupByCommonId(
            ordered,
            "modelSetId",
        );
    }

    private initialiseLayerDefaults(): void {
        const layers: DispLayer[] = dictValuesFromObject(this._layersById);
        for (const layer of layers) {
            layer.initialiseDefaults();
        }
    }

    private groupByCommonId(
        orderedItems: any[],
        groupAttrName: string,
    ): { [id: number]: any[] } {
        let dict = {};

        for (let item of orderedItems) {
            let groupId = item[groupAttrName];
            if (dict[groupId] == null) dict[groupId] = [];

            dict[groupId].push(item);
        }
        return dict;
    }

    // ============================================================================
    // Disp lookup assignments

    private getModelSetId(idOrKey: string | number): number {
        if (typeof idOrKey == "number") return idOrKey;
        return this.modelSetByKey[idOrKey].id;
    }
}
