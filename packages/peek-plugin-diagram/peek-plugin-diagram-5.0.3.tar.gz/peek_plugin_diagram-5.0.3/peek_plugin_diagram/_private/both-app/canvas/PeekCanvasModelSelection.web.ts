import { PeekCanvasConfig } from "./PeekCanvasConfig.web";
import { DispBase, DispBaseT } from "../canvas-shapes/DispBase";
import { Observable, Subject } from "rxjs";

// import 'rxjs/add/operator/takeUntil';

function now(): any {
    return new Date();
}

/**
 * Peek Canvas Model
 *
 * This class stores and manages the model of the NodeCoord and ConnCoord
 * objects that are within the viewable area.
 *
 */

export class PeekCanvasModelSelection {
    // The currently selected coords
    private _selection: DispBaseT[] = [];

    private _selectionChangedSubject = new Subject<DispBaseT[]>();

    private _keysToTryToSelect: string[] = [];

    constructor(
        private model,
        private config: PeekCanvasConfig,
    ) {}

    // -------------------------------------------------------------------------------------
    // reset
    // -------------------------------------------------------------------------------------
    reset() {
        this._selection = [];
        this._keysToTryToSelect = [];
    }

    selectionChangedObservable(): Observable<DispBaseT[]> {
        return this._selectionChangedSubject;
    }

    get hasSelection(): boolean {
        return this._selection.length !== 0;
    }

    selectedDisps(): DispBaseT[] {
        return this._selection;
    }

    applyTryToSelect() {
        for (let key of this._keysToTryToSelect) {
            for (let disp of this.model.viewableDisps()) {
                if (DispBase.key(disp) == key) {
                    this._selection.add(disp); // Don't notify of item select
                    this._keysToTryToSelect.remove(key);
                    break;
                }
            }
        }
    }

    tryToSelectKeys(keys: string[]) {
        this._keysToTryToSelect = keys;
    }

    replaceSelection(objectOrArray: DispBaseT | DispBaseT[] = []) {
        this._selection = [];
        this._selection = this._selection.add(objectOrArray);
        this._selectionChangedSubject.next(this._selection);
        this.config.invalidate();
    }

    addSelection(objectOrArray) {
        this._selection = this._selection.add(objectOrArray);
        this._selectionChangedSubject.next(this._selection);
        this.config.invalidate();
    }

    removeSelection(objectOrArray) {
        this._selection = this._selection.remove(objectOrArray);
        this._selectionChangedSubject.next(this._selection);
        this.config.invalidate();
    }

    clearSelection() {
        this.replaceSelection();
    }
}
