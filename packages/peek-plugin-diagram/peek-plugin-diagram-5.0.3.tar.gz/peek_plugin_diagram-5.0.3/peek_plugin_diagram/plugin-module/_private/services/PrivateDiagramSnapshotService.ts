import { Injectable } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { DiagramSnapshotService } from "../../DiagramSnapshotService";

export interface TakeSnapshotCallbackI {
    (): null | string;
}

/** CoordSetCache
 *
 * This class is responsible for buffering the coord sets in memory.
 *
 * Typically there will be less than 20 of these.
 *
 */
@Injectable()
export class PrivateDiagramSnapshotService
    extends NgLifeCycleEvents
    implements DiagramSnapshotService
{
    private _callback: TakeSnapshotCallbackI | null;

    constructor() {
        super();
    }

    setImageCaptureCallback(callback: TakeSnapshotCallbackI | null): void {
        this._callback = callback;
    }

    snapshotDiagram(): Promise<string | null> {
        if (this._callback == null) return null;

        return Promise.resolve(this._callback());
    }
}
