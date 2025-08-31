import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { Observable } from "rxjs";
import {
    DiagramItemSelectService,
    SelectedItemDetailsI,
} from "../../DiagramItemSelectService";

export { SelectedItemDetailsI } from "../../DiagramItemSelectService";

/** Item Select Service
 *
 * This service notifies the popup service that an item has been selected.
 *
 * THIS IS USED FOR THE NS INTEGRATION
 *
 */
@Injectable()
export class PrivateDiagramItemSelectService extends DiagramItemSelectService {
    private itemSelectSubject = new Subject<SelectedItemDetailsI[]>();

    constructor() {
        super();
    }

    itemsSelectedObservable(): Observable<SelectedItemDetailsI[]> {
        return this.itemSelectSubject.asObservable();
    }

    selectItems(details: SelectedItemDetailsI[]): void {
        this.itemSelectSubject.next(details);
    }
}
