import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { Observable } from "rxjs";
import { DiagramOverrideService } from "../../DiagramOverrideService";
import { DiagramOverrideBase } from "../../override/DiagramOverrideBase";

export interface OverrideUpdateDataI {
    overrides: DiagramOverrideBase[];
    overridesRemoved: boolean;
}

/** Diagram Override Service
 *
 * This service notifies the popup service that an item has been selected.
 *
 */
@Injectable()
export class PrivateDiagramOverrideService extends DiagramOverrideService {
    private overridesUpdatedSubject = new Subject<OverrideUpdateDataI>();

    private appliedOverrides: { [key: string]: DiagramOverrideBase } = {};

    constructor() {
        super();
    }

    get overridesUpdatedObservable(): Observable<OverrideUpdateDataI> {
        if (Object.keys(this.appliedOverrides).length != 0) {
            setTimeout(() => this.notifyOfUpdate(true), 0);
        }

        return this.overridesUpdatedSubject;
    }

    applyOverride(override: DiagramOverrideBase): void {
        this.appliedOverrides[override.key] = override;
        this.notifyOfUpdate(false);
    }

    removeOverride(override: DiagramOverrideBase): void {
        delete this.appliedOverrides[override.key];
        this.notifyOfUpdate(true);
    }

    get allOverrides(): DiagramOverrideBase[] {
        return Object.values(this.appliedOverrides);
    }

    setUsePolylineEdgeColors(enabled: boolean): void {}

    private notifyOfUpdate(removed: boolean): void {
        const overrides = [];
        for (const key of Object.keys(this.appliedOverrides)) {
            overrides.push(this.appliedOverrides[key]);
        }
        this.overridesUpdatedSubject.next({
            overrides: overrides,
            overridesRemoved: removed,
        });
    }
}
