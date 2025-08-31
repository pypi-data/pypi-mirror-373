import { DiagramCoordSetTuple } from "./tuples/DiagramCoordSetTuple";
import { Observable } from "rxjs";

/** Diagram Coord Set Service
 *
 * This service allows other plugins to load coord set tuples from the diagrams offliine
 * cache.
 */
export abstract class DiagramCoordSetService {
    abstract diagramCoordSetTuples(
        modelSetKey: string,
    ): Observable<DiagramCoordSetTuple[]>;

    abstract modelSetKeys(): string[];

    abstract isReadyObservable(): Observable<boolean>;
}
