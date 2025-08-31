import {
    addTupleType,
    deepCopy,
    SerialiseUtil,
    Tuple,
} from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";
import * as moment from "moment";
import { BranchLiveEditTuple } from "./BranchLiveEditTuple";
import { PrivateDiagramLookupService } from "../services/PrivateDiagramLookupService";

// @ts-ignore
import { sortDisps } from "@_peek/peek_plugin_diagram/canvas/PeekCanvasModelUtil.web";
// @ts-ignore
import {
    DispBasePartial,
    DispBaseT,
} from "@_peek/peek_plugin_diagram/canvas-shapes/DispBasePartial";
// @ts-ignore
import { DispGroupPointerPartial } from "@_peek/peek_plugin_diagram/canvas-shapes/DispGroupPointerPartial";
import {
    DispNullPartial,
    DispNullT,
} from "@_peek/peek_plugin_diagram/canvas-shapes/DispNullPartial";

const serUril = new SerialiseUtil();

interface UndoDataI {
    disps: any[];
    anchors: any[];
    updatedByUser: string;
    lastStage: number;
    needsSave: boolean;
    replacementIds: {};
}

export interface BranchLastEditPositionI {
    x: number;
    y: number;
    zoom: number;
    coordSetKey: string;
}

export interface DispChangeResultI {
    disp: DispBaseT;
    modelUpdateRequired: boolean;
}

/** Diagram Branch Tuple
 *
 * This tuple is used internally to transfer branches from the client tuple provider,
 * and transfer branches to the client wrapped in a TupleAction.
 *
 */
@addTupleType
export class BranchTuple extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "BranchTuple";
    private static readonly __ID_NUM = 0;
    private static readonly __COORD_SET_ID_NUM = 1;
    private static readonly __KEY_NUM = 2;
    private static readonly __VISIBLE_NUM = 3;
    private static readonly __UPDATED_DATE = 4;
    private static readonly __CREATED_DATE = 5;
    private static readonly __DISPS_NUM = 6;
    private static readonly __ANCHOR_DISP_KEYS_NUM = 7;
    private static readonly __UPDATED_BY_USER_NUM = 8;
    private static readonly __NEEDS_SAVE_NUM = 9; // Not stored in DB
    private static readonly __LAST_EDIT_POSITION = 10;
    private static readonly __LAST_INDEX_NUM = 10;
    // The list of deltas for this branch
    packedJson__: any[] = [];
    protected override _rawJonableFields = ["packedJson__"];

    // This structure stores IDs that need to be updated, from disps that have been
    // cloned from disps their replacing (their ID is re-assigned)
    // This is only a temporary structure only needed during an editing session.
    private _replacementIds: { [id: number]: number } = {};
    private _dispsById: { [id: number]: DispBaseT } = {};
    private _lastStage = 1;
    private _contextUpdateCallback:
        | ((modelUpdateRequired: boolean) => void)
        | null;

    // Undo / Redo
    private undoQueue: string[] = [];
    private redoQueue: string[] = [];
    private readonly MAX_UNDO = 20;

    constructor() {
        super(BranchTuple.tupleName);
        for (
            let i = this.packedJson__.length;
            i < BranchTuple.__LAST_INDEX_NUM + 1;
            i++
        )
            this.packedJson__.push(null);
    }

    initialiseIndexes(): void {
        this._dispsById = {};
        this._replacementIds = {};

        for (const disp of this.disps) {
            const dispId = DispBasePartial.id(disp);

            if (dispId == null) {
                console.log("ERROR: Disp has no ID");
                console.log(disp);
                continue;
            }
            if (this._dispsById[dispId]) {
                console.log("ERROR: Disp is already loaded");
                console.log(disp);
                continue;
            }
            this._dispsById[dispId] = disp;
        }

        for (const disp of this.disps) {
            // NOTE IDs ARE USED AS TEMPORARY HASH IDs
            // This will hold a temporary ID, unless this branch has been
            // compiled by the server since its last save.
            // Since we don't know what the hash ids will be.
            const replacesHashId = DispBasePartial.replacesHashId(disp);
            if (!replacesHashId) {
                continue;
            }

            const temporaryIdDisp = this._dispsById[replacesHashId];
            if (temporaryIdDisp) {
                this._replacementIds[replacesHashId] = DispBasePartial.id(disp);
            }
        }
    }

    get needsSave(): boolean {
        return this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM];
    }

    get id(): number {
        return this.packedJson__[BranchTuple.__ID_NUM];
    }

    get coordSetId(): number {
        return this.packedJson__[BranchTuple.__COORD_SET_ID_NUM];
    }

    get key(): string {
        return this.packedJson__[BranchTuple.__KEY_NUM];
    }

    get updatedByUser(): string {
        return this.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM];
    }

    set updatedByUser(val: string) {
        this.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM] = val;
    }

    get lastEditPosition(): BranchLastEditPositionI | null {
        const jsonStr = this.packedJson__[BranchTuple.__LAST_EDIT_POSITION];
        if (jsonStr == null || jsonStr.length == 0) {
            return null;
        }
        return JSON.parse(jsonStr);
    }

    set lastEditPosition(position: BranchLastEditPositionI) {
        this.packedJson__[BranchTuple.__LAST_EDIT_POSITION] =
            JSON.stringify(position);
    }

    get disps(): any[] {
        return this._array(BranchTuple.__DISPS_NUM).slice();
    }

    get anchorDispKeys(): string[] {
        return this._array(BranchTuple.__ANCHOR_DISP_KEYS_NUM).slice();
    }

    get visible(): boolean {
        return this.packedJson__[BranchTuple.__VISIBLE_NUM];
    }

    set visible(value: boolean) {
        this.packedJson__[BranchTuple.__VISIBLE_NUM] = value;
    }

    get updatedDate(): Date | null {
        const packedDate = this.packedJson__[BranchTuple.__UPDATED_DATE];
        if (packedDate == null) {
            return packedDate;
        }

        return serUril.fromStr(packedDate, SerialiseUtil.T_DATETIME);
    }

    get createdDate(): Date {
        return serUril.fromStr(
            this.packedJson__[BranchTuple.__CREATED_DATE],
            SerialiseUtil.T_DATETIME,
        );
    }

    static createBranch(coordSetId: number, branchKey: string): any {
        const branch = new BranchTuple();
        branch.packedJson__[BranchTuple.__ID_NUM] = this._makeUniqueId();
        branch.packedJson__[BranchTuple.__COORD_SET_ID_NUM] = coordSetId;
        branch.packedJson__[BranchTuple.__KEY_NUM] = branchKey;
        branch.packedJson__[BranchTuple.__VISIBLE_NUM] = true;
        branch.setUpdatedDate(null);
        branch.setCreatedDate(new Date());
        branch.packedJson__[BranchTuple.__DISPS_NUM] = [];
        branch.packedJson__[BranchTuple.__ANCHOR_DISP_KEYS_NUM] = [];
        branch.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM] = null;
        branch.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = false;
        branch.resetUndo();
        return branch;
    }

    static unpackJson(packedJsonStr: string): BranchTuple {
        // Create the new object
        const newSelf = new BranchTuple();
        newSelf.packedJson__ = JSON.parse(packedJsonStr);
        newSelf.assignIdsToDisps();
        newSelf.sortDisps();
        newSelf.resetUndo();
        return newSelf;
    }

    private static _makeUniqueId(index = -1): any {
        return <any>`NEW_${new Date().getTime()}_${index}`;
    }

    private static _setNewDispId(disp: DispBaseT, index: number): void {
        let newId = this._makeUniqueId(index);
        if (DispBasePartial.id(disp) == null)
            DispBasePartial.setId(disp, newId);
        if (DispBasePartial.hashId(disp) == null)
            DispBasePartial.setHashId(disp, newId);
    }

    branchHasBeenSaved(): void {
        this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = false;
    }

    addStage(): number {
        return this._lastStage++;
    }

    /** Add or Update Disps
     *
     * This method adds an array of disps to the branch.
     *
     * @param disps An array of disps to add.
     * @param preventModelUpdate Prevents this update from calling model compile.
     */
    addOrUpdateDisps(disps: any, preventModelUpdate = false): any[] {
        let modelUpdateRequired = false;
        let returnedDisps = [];

        for (let disp of disps) {
            let result = this.addOrUpdateSingleDisp(disp);
            modelUpdateRequired =
                modelUpdateRequired || result.modelUpdateRequired;
            returnedDisps.push(result.disp);
        }

        for (let disp of returnedDisps) this.updateReplacedIds(disp);

        this.touchUpdateDate(modelUpdateRequired && !preventModelUpdate);
        return returnedDisps;
    }

    /** Add or Update Disp
     *
     * This method adds the disp to the branch if it's new.
     *
     * If the disp is existing, but in a different stage, it clones and returns the disp
     * in the new stage.
     *
     * @param disp
     * @param preventModelUpdate Prevents this update from calling model
     * compile.
     */
    addOrUpdateDisp(disp: any, preventModelUpdate = false): any {
        const result = this.addOrUpdateSingleDisp(disp);
        this.updateReplacedIds(result.disp);
        this.touchUpdateDate(result.modelUpdateRequired && !preventModelUpdate);
        return result.disp;
    }

    // @ts-ignore
    isDispInBranch(disp: any): boolean {
        return (
            this._dispsById[DispBasePartial.id(disp)] != null ||
            this._replacementIds[DispBasePartial.id(disp)] != null
        );
    }

    /** Add New Disps
     *
     * This method adds newly created disps to tbe branch in bulk.
     *
     * @param disps
     */
    addNewDisps(disps: any[]): void {
        const array = this._array(BranchTuple.__DISPS_NUM);

        for (const disp of disps) {
            BranchTuple._setNewDispId(disp, array.length);
            DispBasePartial.setBranchStage(disp, this._lastStage);
            this._dispsById[DispBasePartial.id(disp)] = disp;
            array.push(disp);
        }
        this.touchUpdateDate(true);
    }

    removeDisps(disps: any[]): void {
        const dispIdsToRemove: { [dispId: string]: DispBaseT } = {};
        for (let disp of disps) {
            dispIdsToRemove[DispBasePartial.id(disp)] = disp;
        }

        const array = this._array(BranchTuple.__DISPS_NUM);
        const branchDispsToBeConvertedToNullDisps: DispBaseT[] = [];

        // Filter out disps in this branch that we're deleting
        // If the disp we're deleting replacing anoter disp (not in this branch)
        //      make a note of that.
        this.packedJson__[BranchTuple.__DISPS_NUM] = array.filter((disp) => {
            let id = DispBasePartial.id(disp);
            if (dispIdsToRemove[id] != null) {
                if (DispBasePartial.replacesHashId(disp) != null)
                    branchDispsToBeConvertedToNullDisps.push(disp);
                delete dispIdsToRemove[id];
                return false;
            }
            return true;
        });

        // Update the dispId dict to remove the disps we just filtered out
        this.assignIdsToDisps();

        // For all the Disps that are not part of this branch, we need to add a DispNull
        // to make it's deletion

        const nullDispsToCreate: DispBaseT[] = [];

        function createNullDisp(
            dispToDelete: DispBaseT,
            replacesHashId: string,
        ) {
            if (dispToDelete.bounds == null) {
                throw new Error("Can not delete a disp with no bounds");
            }

            const nullDisp = <DispNullT>{
                // Type
                _tt: DispBasePartial.TYPE_DN,

                // Level
                le: dispToDelete.le,
                lel: dispToDelete.lel,

                // Layer
                la: dispToDelete.la,
                lal: dispToDelete.lal,
            };

            DispNullPartial.setGeomFromBounds(nullDisp, dispToDelete.bounds);
            DispBasePartial.setReplacesHashId(nullDisp, replacesHashId);
            nullDispsToCreate.push(<DispBaseT>nullDisp);
        }

        // For all the Disps that are not part of this branch, we need to add a DispNull
        // to make it's deletion
        // Create NULL disps for disps being deleted that are not part of this branch
        for (let dispId of Object.keys(dispIdsToRemove)) {
            const disp = dispIdsToRemove[dispId];
            createNullDisp(disp, DispBasePartial.hashId(disp));
        }

        // For all disps that are part of this branch, but replace other disps,
        // Create NULL disps for disps in this branch that replace other disps
        for (let disp of branchDispsToBeConvertedToNullDisps) {
            createNullDisp(disp, DispBasePartial.replacesHashId(disp));
        }

        if (nullDispsToCreate.length != 0) {
            this.addNewDisps(nullDispsToCreate);
        } else {
            this.touchUpdateDate(false);
        }
    }

    addAnchorDispKey(key: string): void {
        let anchors = this._array(BranchTuple.__ANCHOR_DISP_KEYS_NUM);
        if (anchors.filter((k) => k == key).length != 0) {
            return;
        }

        this.touchUpdateDate(false);
        anchors.push(key);
    }

    touchUpdateDate(modelUpdateRequired: boolean = false): void {
        this.sortDisps();
        this.setNeedsSave();
        this.setUpdatedDate(new Date());
        if (this._contextUpdateCallback != null) {
            this._contextUpdateCallback(modelUpdateRequired);
        }
    }

    touchUndo(): void {
        const current = this.serialiseDisps();

        // If there is no change, queue nothing
        const len = this.undoQueue.length;
        if (len != 0 && this.undoQueue[len - 1] == current) {
            return;
        }

        this.undoQueue.push(current);
        this.resetRedo();

        while (this.undoQueue.length > this.MAX_UNDO) this.undoQueue.shift();
    }

    get canUndo(): boolean {
        return this.undoQueue.length > 1;
    }

    doUndo(lookupService: PrivateDiagramLookupService): void {
        if (this.undoQueue.length <= 1) {
            return;
        }

        const len = this.undoQueue.length;
        this.redoQueue.push(this.undoQueue.pop());
        this.restoreSerialisedDisps(this.undoQueue[len - 2]);

        this.linkDisps(lookupService);
        this.touchUpdateDate(true);
    }

    get canRedo(): boolean {
        return this.redoQueue.length !== 0;
    }

    doRedo(lookupService: PrivateDiagramLookupService): void {
        if (this.redoQueue.length == 0) {
            return;
        }

        const redo = this.redoQueue.pop();
        this.undoQueue.push(redo);
        this.restoreSerialisedDisps(redo);

        this.linkDisps(lookupService);
        this.touchUpdateDate(true);
    }

    override toJsonField(
        value: any,
        jsonDict: { [key: string]: any } | null = null,
        name: string | null = null,
    ): any {
        if (name != "packedJson__")
            return Tuple.prototype.toJsonField(value, jsonDict, name);

        const convertedValue = deepCopy(
            value,
            DispBasePartial.DEEP_COPY_FIELDS_TO_IGNORE,
        );

        const disps = convertedValue[BranchTuple.__DISPS_NUM];

        this.cleanClonedDisps(disps);

        /* Now assign the value and it's value type if applicable */
        if (name != null && jsonDict != null) jsonDict[name] = convertedValue;

        return convertedValue;
    }

    linkDisps(lookupService: PrivateDiagramLookupService) {
        for (let disp of this.disps) {
            lookupService._linkDispLookups(disp);
        }
    }

    setContextUpdateCallback(
        contextUpdateCallback: ((modelUpdateRequired: boolean) => void) | null,
    ) {
        this._contextUpdateCallback = contextUpdateCallback;
    }

    applyLiveUpdate(liveEditTuple: BranchLiveEditTuple): boolean {
        let liveUpdateTuple = liveEditTuple.branchTuple;

        if (
            this.updatedDate == null ||
            moment(this.updatedDate).isBefore(liveUpdateTuple.updatedDate) ||
            liveEditTuple.updateFromSave
        ) {
            this.packedJson__ = liveUpdateTuple.packedJson__;
            this.assignIdsToDisps();
            this.resetUndo();
            this.resetRedo();
            return true;
        }
        return false;
    }

    private assignIdsToDisps(): void {
        // @ts-ignore
        const array = this._array(BranchTuple.__DISPS_NUM);
        for (let i = 0; i < array.length; ++i) {
            const disp = array[i];
            BranchTuple._setNewDispId(disp, i);
            this._dispsById[DispBasePartial.id(disp)] = disp;
            if (this._lastStage < DispBasePartial.branchStage(disp))
                this._lastStage = DispBasePartial.branchStage(disp);
        }
    }

    private _array(num: number): any[] {
        if (this.packedJson__[num] == null) this.packedJson__[num] = [];
        return this.packedJson__[num];
    }

    private resetUndo(): void {
        this.undoQueue = [this.serialiseDisps()];
    }

    private resetRedo(): void {
        this.redoQueue = [];
    }

    private setNeedsSave(): void {
        this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = true;
    }

    private updateReplacedIds(disp: DispBaseT) {
        // @ts-ignore
        const newGroupId = this._replacementIds[DispBasePartial.groupId(disp)];
        if (newGroupId != null) {
            DispBasePartial.setGroupId(disp, newGroupId);
        }
    }

    private addOrUpdateSingleDisp(disp: any): DispChangeResultI {
        // @ts-ignore
        const array = this._array(BranchTuple.__DISPS_NUM);

        // If we've already replaced this Disp, then just return the replacement disp
        // This can happen when the select delegates call addOrUpdate disp multiple
        // times. (They have a selected and related array)
        if (this._replacementIds[DispBasePartial.id(disp)] != null) {
            let newId = this._replacementIds[DispBasePartial.id(disp)];
            return { disp: this._dispsById[newId], modelUpdateRequired: false };
        }

        // Find out if the disp is in this branch
        let dispInBranch = this._dispsById[DispBasePartial.id(disp)];

        // If the Disp has an ID and it's not in this branch, then:
        // 1) we make a copy of the disp
        // 2) we set its "replacesHashId" to the "hashId" it's replacing.
        if (DispBasePartial.id(disp) != null && dispInBranch == null) {
            let branchDisp = DispBasePartial.cloneDisp(disp);

            DispBasePartial.setReplacesHashId(
                branchDisp,
                DispBasePartial.hashId(disp),
            );
            DispGroupPointerPartial.setTargetGroupId(branchDisp as any, null);
            DispBasePartial.setHashId(branchDisp, null);

            // Deal with the new updated ID
            DispBasePartial.setId(branchDisp, null);
            BranchTuple._setNewDispId(branchDisp, array.length);
            this._replacementIds[DispBasePartial.id(disp)] =
                DispBasePartial.id(branchDisp);

            disp = branchDisp;
        }

        BranchTuple._setNewDispId(disp, array.length);

        if (dispInBranch == null) {
            DispBasePartial.setBranchStage(disp, this._lastStage);
            this._dispsById[DispBasePartial.id(disp)] = disp;
            array.push(disp);
            return { disp: disp, modelUpdateRequired: true };
        }

        if (
            DispBasePartial.branchStage(dispInBranch) ==
            DispBasePartial.branchStage(disp)
        ) {
            return { disp: disp, modelUpdateRequired: false };
        }

        // Else, it's a new stage, clone the disp.

        this._dispsById[DispBasePartial.id(disp)] = disp;
        array.push(disp);
        return { disp: disp, modelUpdateRequired: true };
    }

    private sortDisps(): void {
        const array = this._array(BranchTuple.__DISPS_NUM);
        this.packedJson__[BranchTuple.__DISPS_NUM] = sortDisps(array);
    }

    private setUpdatedDate(value: Date | null): void {
        if (value == null) {
            this.packedJson__[BranchTuple.__UPDATED_DATE] = null;
        } else
            this.packedJson__[BranchTuple.__UPDATED_DATE] =
                serUril.toStr(value);
    }

    private setCreatedDate(value: Date): void {
        this.packedJson__[BranchTuple.__CREATED_DATE] = serUril.toStr(value);
    }

    private serialiseDisps(): string {
        // @ts-ignore

        const disps = deepCopy(
            this._array(BranchTuple.__DISPS_NUM),
            DispBasePartial.DEEP_COPY_FIELDS_TO_IGNORE,
        );
        this.cleanClonedDisps(disps);

        let data: UndoDataI = {
            disps: disps,
            anchors: this.anchorDispKeys,
            updatedByUser: this.updatedByUser,
            lastStage: this._lastStage,
            needsSave: this.needsSave,
            replacementIds: this._replacementIds,
        };

        return JSON.stringify(data);
    }

    private restoreSerialisedDisps(undoJsonStr: string): void {
        const data: UndoDataI = JSON.parse(undoJsonStr);

        this.packedJson__[BranchTuple.__DISPS_NUM] = data.disps;
        this.packedJson__[BranchTuple.__ANCHOR_DISP_KEYS_NUM] = data.anchors;
        this.packedJson__[BranchTuple.__UPDATED_BY_USER_NUM] =
            data.updatedByUser;
        this.packedJson__[BranchTuple.__NEEDS_SAVE_NUM] = data.needsSave;

        this._replacementIds = data.replacementIds;
        this._lastStage = data.lastStage;
        this.assignIdsToDisps();
        this.initialiseIndexes();
    }

    private cleanClonedDisps(disps: any[]): void {
        for (let disp of disps) {
            for (let key of Object.keys(disp)) {
                let dispval = disp[key];

                // Nulls are not included
                if (dispval == null) delete disp[key];
                // Delete all the linked lookups, we just want the IDs
                else if (dispval["__rst"] != null)
                    // VortexJS Serialise Class Type
                    delete disp[key];
            }
        }
    }
}
