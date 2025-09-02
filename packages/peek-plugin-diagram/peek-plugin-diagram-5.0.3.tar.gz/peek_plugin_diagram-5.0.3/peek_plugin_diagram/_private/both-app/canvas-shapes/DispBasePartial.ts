import {
    DispLayer,
    DispLevel,
} from "@peek/peek_plugin_diagram/_private/lookups";
import { PeekCanvasBounds } from "@peek/peek_plugin_diagram/_private/PeekCanvasBounds";
import { deepCopy } from "@synerty/vortexjs";

export interface PointI {
    x: number;
    y: number;
}

export enum DispHandleTypeE {
    freeRotate,
    snapRotate,
    movePoint,
    resizeShape,
    primaryAction,
}

export interface DispHandleI {
    disp: DispBaseT;
    center: PointI;
    handleType: DispHandleTypeE;
    box?: PeekCanvasBounds;
    handleIndex?: number | null;
    lastDeltaPoint?: PointI | null;
}

export enum DispType {
    ellipse,
    polygon,
    polyline,
    text,
    group,
    groupPointer,
    edgeTemplate,
    null_,
    curvedText,
}

// ---------------------
// Begin the action definitions

export enum DispActionEnum {
    none, // Or null
    positionOn,
}

export interface DispActionPositionOnDataT {
    k: string; // coordSetKey, shortened because this is
    x: number;
    y: number;
    z: number; // Zoom
}

// --------------------
// Begin the Disp definitions

/** This type defines the list of points for geometry **/
export type PointsT = number[];

export interface DispBaseT {
    // The type of the disp
    _tt: string;

    // The ID of the disp
    id: number;

    // Z Order
    z: number;

    // This is the unique hash of the contents of this disp within this coordSetId.
    hid: string;

    // Key
    k: string | null;

    // Group ID
    gi: number | null;

    // Branch ID
    bi: number | null;

    // Branch Stage
    bs: number | null;

    // Replaces Disp HashId
    rid: string | null;

    // Level
    le: number;
    lel: DispLevel;

    // Layer
    la: number;
    lal: DispLayer;

    // Is Selectable
    s: boolean;

    // Is Overlay
    o: boolean;

    // Action
    a: DispActionEnum | null;

    // Data (stringified JSON)
    d: string | null;

    // Geomoetry
    g: PointsT;

    // bounds, this is assigned during the rendering process
    // COMPUTED PROPERTY, it's computed somewhere
    bounds: PeekCanvasBounds | null;

    // The disp group that this shape belongs to.
    // Set by the model compiler
    // COMPUTED PROPERTY, it's computed somewhere
    dispGroup: any | null;
}

export abstract class DispBasePartial {
    static readonly TYPE_DT = "DT";
    static readonly TYPE_DCT = "DCT";
    static readonly TYPE_DPG = "DPG";
    static readonly TYPE_DPL = "DPL";
    static readonly TYPE_DE = "DE";
    static readonly TYPE_DG = "DG";
    static readonly TYPE_DGP = "DGP";
    static readonly TYPE_DET = "DET";
    static readonly TYPE_DN = "DN";

    static readonly DEEP_COPY_FIELDS_TO_IGNORE = [
        "bounds",
        "disps",
        "dispGroup",
        "lel", // DispLevel
        "lal", // DispLayer
        "fsl", // DispTextStyle
        "cl", // DispColor
        "bcl", // DispColor
        "ecl", // DispColor
        "fcl", // DispColor
        "lcl", // DispColor
        "lsl", // DispLineStyle
    ];
    protected static _typeMapInit = false;
    protected static _typeMap = {};

    // Lazy instantiation, because the string types are defined elsewhere
    protected static get typeMap() {
        if (!DispBasePartial._typeMapInit) {
            DispBasePartial._typeMapInit = true;
            DispBasePartial._typeMap[DispBasePartial.TYPE_DT] = [
                DispType.text,
                "Text",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DCT] = [
                DispType.curvedText,
                "CurvedText",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DPG] = [
                DispType.polygon,
                "Polygon",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DPL] = [
                DispType.polyline,
                "Polyline",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DE] = [
                DispType.ellipse,
                "Ellipse",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DG] = [
                DispType.group,
                "Group",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DGP] = [
                DispType.groupPointer,
                "GroupPointer",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DET] = [
                DispType.edgeTemplate,
                "EdgeTemplate",
            ];
            DispBasePartial._typeMap[DispBasePartial.TYPE_DN] = [
                DispType.null_,
                "Deleted Shape",
            ];
        }

        return DispBasePartial._typeMap;
    }

    static typeOf(disp): DispType {
        return DispBasePartial.typeMap[disp._tt][0];
    }

    static id(disp: DispBaseT): number {
        return disp.id;
    }

    static setId(disp: DispBaseT, value: number): void {
        disp.id = value;
    }

    static branchId(disp: DispBaseT): number {
        return disp.bi;
    }

    static branchStage(disp: DispBaseT): number {
        return disp.bs;
    }

    static setBranchStage(disp: DispBaseT, value: number): void {
        disp.bs = value;
    }

    static levelId(disp: DispBaseT): number {
        return disp.le;
    }

    static level(disp: DispBaseT): DispLevel {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.lel;
    }

    static setLevel(disp: DispBaseT, val: DispLevel): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.lel = val;
        disp.le = val == null ? null : val.id;
    }

    static layerId(disp: DispBaseT): number {
        return disp.la;
    }

    static layer(disp: DispBaseT): DispLayer {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        return disp.lal;
    }

    static setLayer(disp: DispBaseT, val: DispLayer): void {
        // This is set from the short id in PrivateDiagramLookupService._linkDispLookups
        disp.lal = val;
        disp.la = val == null ? null : val.id;
    }

    static zOrder(disp: DispBaseT): number {
        return disp.z || 0; // defaults to 0
    }

    static setZOrder(disp: DispBaseT, value: number): void {
        disp.z = value;
    }

    static hashId(disp: DispBaseT): string {
        return disp.hid;
    }

    static setHashId(disp: DispBaseT, value: string): void {
        disp.hid = value;
    }

    static replacesHashId(disp: DispBaseT): string {
        return disp.rid;
    }

    static setReplacesHashId(disp: DispBaseT, value: string): void {
        disp.rid = value;
    }

    static groupId(disp: DispBaseT): number | null {
        return disp.gi;
    }

    static setGroupId(disp: DispBaseT, val: number): void {
        disp.gi = val;
    }

    static cloneDisp(
        disp: DispBaseT,
        options: { resetUniques?: boolean } = {},
    ): DispBaseT {
        let copy = deepCopy(disp, DispBasePartial.DEEP_COPY_FIELDS_TO_IGNORE);

        // Copy over the lookup tuples, as they would have been cloned as well.
        for (let key of Object.keys(disp)) {
            if (disp[key] != null && disp[key]["__rst"] != null)
                copy[key] = disp[key];
        }

        if (options.resetUniques) {
            delete copy.id; // Base: Id
            delete copy.hid; // Base: Hash ID
            delete copy.rid; // Base: Replaces Hash ID
            delete copy.k; // Base: Key
            delete copy.bi; // Base: Branch ID
            delete copy.bs; // Base: Branch Stage
            // delete copy.gi; // Base: Group ID
            delete copy.sk; // Polyline: Start Key
            delete copy.ek; // Polyline: End Key
        }

        return copy;
    }
}
