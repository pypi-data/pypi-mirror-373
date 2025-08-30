import { BranchDetailTuple } from "@peek/peek_plugin_branch";
import { Observable } from "rxjs";

export interface DiagramBranchDetailsI {
    modelSetKey: string;
    coordSetKey: string;
    branchKey: string;
    updatedByUser: string;
    createdDate: Date;
    updatedDate: Date | null;
    anchorKeys: string[];
}

/** Diagram Branch Service
 *
 * This service notifies the popup service that an item has been selected.
 *
 */
export abstract class DiagramBranchService {
    constructor() {}

    abstract setVisibleBranches(commonBranches: BranchDetailTuple[]): void;

    abstract getVisibleBranches(): BranchDetailTuple[];

    abstract getActiveBranchDetails(): Promise<DiagramBranchDetailsI | null>;

    abstract startEditing(
        modelSetKey: string,
        coordSetKey: string,
        branchKey: string,
    ): Promise<void>;

    abstract startEditingObservable(): Observable<void>;

    abstract stopEditingObservable(): Observable<void>;
}
