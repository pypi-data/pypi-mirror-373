import { Observable } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { OfflineCacheLoaderStatusTuple } from "@peek/peek_core_device";
import { BranchIndexResultI } from "./BranchIndexLoaderService";

export abstract class BranchIndexLoaderServiceA extends NgLifeCycleEvents {
    constructor() {
        super();
    }

    abstract isReady(): boolean;

    abstract isReadyObservable(): Observable<boolean>;

    abstract statusObservable(): Observable<OfflineCacheLoaderStatusTuple>;

    abstract status(): OfflineCacheLoaderStatusTuple;

    abstract getBranches(
        modelSetKey: string,
        coordSetId: number | null,
        keys: string[],
    ): Promise<BranchIndexResultI>;
}
