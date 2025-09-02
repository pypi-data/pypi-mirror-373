import { Injectable } from "@angular/core";
import { Observable, Subject } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

export interface ContextMenuPopupI {
    x: number;
    y: number;
}
/** Context Menu Service
 *
 * This class is responsible for coordinating the context menu popups
 *
 */
@Injectable()
export class ContextMenuService extends NgLifeCycleEvents {
    private openSubject = new Subject<ContextMenuPopupI>();

    constructor() {
        super();
    }
    get openObservable(): Observable<ContextMenuPopupI> {
        return this.openSubject.asObservable();
    }

    doOpenMenu(info: ContextMenuPopupI): void {
        this.openSubject.next(info);
    }
}
