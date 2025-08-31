import { Observable } from "rxjs";

export interface SelectedItemDetailsI {
    modelSetKey: string;
    coordSetKey: string;
    dispKey: string;
    dispData: {};
}

/** Item Select Service
 *
 * This service allows other plugins to be notified when items are selected.
 *
 *
 */
export abstract class DiagramItemSelectService {
    /** itemSelectObservable
     *
     * This observable is fired when an item on the diagram is selected
     */
    abstract itemsSelectedObservable(): Observable<SelectedItemDetailsI[]>;
}
