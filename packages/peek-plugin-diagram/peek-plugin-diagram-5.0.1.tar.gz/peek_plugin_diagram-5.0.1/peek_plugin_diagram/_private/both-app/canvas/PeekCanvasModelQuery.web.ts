import {
    DispBase,
    DispBaseT,
    DispType,
    PointI,
} from "../canvas-shapes/DispBase";
import { DispPolyline } from "../canvas-shapes/DispPolyline";
import { DispGroupPointerT } from "../canvas-shapes/DispGroupPointer";
import { DispPolygon } from "../canvas-shapes/DispPolygon";

// import 'rxjs/add/operator/takeUntil';

export interface PolylineEnd {
    isStart: boolean;
    disp: any;
}

export interface DispFilterCallableT {
    (disp: DispBaseT): boolean;
}

/**
 * Peek Canvas Model
 *
 * This class stores and manages the model of the NodeCoord and ConnCoord
 * objects that are within the viewable area.
 *
 */

export class PeekCanvasModelQuery {
    constructor(private model) {}

    // -------------------------------------------------------------------------------------
    // Display Items
    // -------------------------------------------------------------------------------------

    get viewableDisps(): any[] {
        return this.model.viewableDisps();
    }

    get selectableDisps(): any[] {
        // Null shapes should never have selectable set anyway
        return this.viewableDisps.filter(
            (disp) =>
                DispBase.isSelectable(disp) &&
                DispBase.typeOf(disp) != DispType.null_ &&
                DispBase.layer(disp).calculateEffectiveSelectability(),
        );
    }

    get editableShapes(): any[] {
        const allLayers = this.model.lookupService.layersOrderedByOrder(
            this.model.config.controller.modelSetKey,
        );

        const editableLayerIds = new Set<number>();
        for (const layer of allLayers) {
            if (layer.calculateEffectiveEditorEditable()) {
                editableLayerIds.add(layer.id);
            }
        }

        return this.model.viewableDisps().filter((shape: DispBaseT) => {
            return editableLayerIds.has(DispBase.layerId(shape));
        });
    }

    get selectedDisps(): any[] {
        return this.model.selection.selectedDisps();
    }

    get dispsInSelectedGroups(): any[] {
        return this.dispsForGroups(this.selectedDisps);
    }

    sortBySelectionPriority(disps: DispBaseT[]): any[] {
        function cmp(disp1: DispBaseT, disp2: DispBaseT): number {
            if (
                DispBase.typeOf(disp1) == DispType.groupPointer &&
                DispBase.typeOf(disp2) != DispType.groupPointer
            )
                return 1;

            if (
                DispBase.typeOf(disp1) == DispType.polygon &&
                DispBase.typeOf(disp2) != DispType.polygon
            )
                return 1;

            // Put all the null bounds at one end
            if (disp1.bounds && !disp2.bounds) return 1;

            if (!disp1.bounds && disp2.bounds) return -1;

            // Bigger bounds come first
            return disp1.bounds.area() - disp1.bounds.area();
        }

        return disps.sort(cmp);
    }

    sortByDistanceFromCenter(disps, point: PointI): any[] {
        const lazyDists = {};

        function lazyGetDist(disp) {
            if (disp.bounds == null) return 99999999;
            let dist = lazyDists[DispBase.id(disp)];
            if (dist != null) return dist;
            return (lazyDists[DispBase.id(disp)] =
                disp.bounds.distanceFromPoint(point));
        }

        function cmp(disp1, disp2): number {
            return lazyGetDist(disp1) - lazyGetDist(disp2);
        }

        return disps.sort(cmp);
    }

    filterForVisibleDisps(
        disps,
        zoom,
        includeShapesWithNoColor = false,
        includeShapesWithNoKey: boolean = true,
    ): any[] {
        function check(disp): boolean {
            if (DispBase.typeOf(disp) == DispType.null_) {
                return false;
            }

            if (!includeShapesWithNoColor && !DispBase.hasColor(disp)) {
                return false;
            }

            if (!includeShapesWithNoKey && !DispBase.key(disp)) {
                return false;
            }

            if (!DispBase.layer(disp).calculateEffectiveVisibility()) {
                return false;
            }

            const level = DispBase.level(disp);
            return level.isVisibleAtZoom(zoom);
        }

        return disps.filter(check);
    }

    filterForDispsContainingPoint(
        disps,
        zoom: number,
        margin: number,
        point: PointI,
        useBoxContainsForPolygons: boolean,
    ): any[] {
        margin = margin / zoom;
        return disps.filter((d) => {
            if (
                DispBase.typeOf(d) == DispType.polygon &&
                !useBoxContainsForPolygons
            ) {
                return DispPolygon.contains(d, point, margin);
            }
            if (DispBase.typeOf(d) == DispType.polyline) {
                return DispPolyline.contains(d, point, margin);
            }
            if (DispBase.typeOf(d) == DispType.curvedText) {
                return DispPolyline.contains(d, point, margin);
            }
            return d.bounds && d.bounds.contains(point.x, point.y, margin);
        });
    }

    keyOfDisps(disps: any[]): string[] {
        let keys = [];
        for (let disp of disps) {
            if (DispBase.key(disp) != null) keys.push(DispBase.key(disp));
        }
        return keys;
    }

    uniqueDisps(disps: any[]): string[] {
        const ids = {};
        return disps.filter((d) =>
            ids[d.id] === true ? false : (ids[d.id] = true),
        );
    }

    uniquePolylineEnds(ends: PolylineEnd[]): PolylineEnd[] {
        const ids = {};
        return ends.filter((d) =>
            ids[d.disp.id] === true ? false : (ids[d.disp.id] = true),
        );
    }

    dispsForKeys(keys: string[]): any[] {
        let keyDict = {};
        for (let key of keys) keyDict[key] = true;

        let resultDisps = [];
        for (let disp of this.viewableDisps) {
            if (keyDict[DispBase.key(disp)] != null) resultDisps.push(disp);
        }

        return resultDisps;
    }

    /** Disp Group for Disp
     *
     * Return the DispGroupPointer that a disp belongs to.
     * NOTE: This is an O(N) approach
     * @param disp
     */
    dispGroupForDisp(disp: DispBaseT): DispGroupPointerT | null {
        let groupId = DispBase.groupId(disp);

        if (groupId == null) return null;

        for (let iterDisp of this.model.viewableDisps()) {
            if (DispBase.id(iterDisp) == groupId) return iterDisp;
        }
        return null;
    }

    dispsInSameGroup(refDisp): any[] {
        return this.dispsForGroups([refDisp]);
    }

    dispsForGroups(disps: any[]): any[] {
        const result = [];
        const selectedGroupIds = {};

        for (let disp of disps) {
            // DispGroup and DispGroupPtrs are not selectable
            selectedGroupIds[DispBase.id(disp)] = true;
            if (DispBase.groupId(disp) != null)
                selectedGroupIds[DispBase.groupId(disp)] = true;
        }

        const dispIdsAdded = {}; // return a unique list.
        for (let disp of this.viewableDisps) {
            if (dispIdsAdded[DispBase.id(disp)]) continue;
            dispIdsAdded[DispBase.id(disp)] = true;

            if (selectedGroupIds[DispBase.groupId(disp)] === true)
                result.push(disp);
            else if (selectedGroupIds[DispBase.id(disp)] === true)
                result.push(disp);
        }

        return result;
    }

    decentAndAddDisps(
        disps: DispBaseT[],
        outDisps: DispBaseT[] = [],
    ): DispBaseT[] {
        for (let disp of disps) {
            outDisps.push(disp);
            if (disp["disps"] != null)
                this.decentAndAddDisps(disp["disps"], outDisps);
        }
        return outDisps;
    }

    polylinesConnectedToDispKey(keys: string[]): PolylineEnd[] {
        let result: PolylineEnd[] = [];
        let keysDict = {};

        for (let key of keys) {
            keysDict[key] = true;
        }

        for (let disp of this.viewableDisps) {
            let startKey = DispPolyline.startKey(disp);
            let endKey = DispPolyline.endKey(disp);

            if (startKey != null && keysDict[startKey] === true)
                result.push({ isStart: true, disp: disp });
            else if (endKey != null && keysDict[endKey] === true)
                result.push({ isStart: false, disp: disp });
        }

        return result;
    }

    polylinesConnectedToPoint(points: PointI[]): PolylineEnd[] {
        let result: PolylineEnd[] = [];
        let pointsDict = {};

        for (let point of points) {
            pointsDict[`${point.x}x${point.y}`] = true;
        }

        for (let disp of this.viewableDisps) {
            if (DispBase.typeOf(disp) != DispType.polyline) continue;

            let fp = DispPolyline.firstPoint(disp);
            let lp = DispPolyline.lastPoint(disp);

            if (pointsDict[`${fp.x}x${fp.y}`] === true)
                result.push({ isStart: true, disp: disp });
            else if (pointsDict[`${lp.x}x${lp.y}`] === true)
                result.push({ isStart: false, disp: disp });
        }

        return result;
    }

    closestDispToPoint(
        x,
        y,
        dispFiltCallable: DispFilterCallableT | null = null,
    ): DispBaseT | null {
        let closestDisp = null;
        let closestDispDistance = null;

        for (let disp of this.viewableDisps) {
            if (disp.bounds == null) continue;

            if (dispFiltCallable != null && !dispFiltCallable(disp)) continue;

            let distance = disp.bounds.distanceFromPoint({ x, y });
            if (closestDisp == null || distance < closestDispDistance) {
                closestDisp = disp;
                closestDispDistance = distance;
            }
        }

        return closestDisp;
    }
}
