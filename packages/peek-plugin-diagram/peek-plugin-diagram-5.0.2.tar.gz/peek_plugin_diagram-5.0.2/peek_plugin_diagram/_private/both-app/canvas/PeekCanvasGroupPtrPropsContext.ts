import { DispGroupT } from "../canvas-shapes/DispGroup";
import {
    DispGroupPointer,
    DispGroupPointerT,
} from "../canvas-shapes/DispGroupPointer";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch/BranchTuple";
import { PeekCanvasModel } from "./PeekCanvasModel.web";

export class PeekCanvasGroupPtrPropsContext {
    constructor(
        private model: PeekCanvasModel,
        private dispGroupPtr: DispGroupPointerT,
        private lookupService: PrivateDiagramLookupService,
        private branchTuple: BranchTuple,
    ) {}

    get targetDispGroupCoordSetId(): number | null {
        return DispGroupPointer.targetGroupCoordSetId(this.dispGroupPtr);
    }

    get targetDispGroupName(): string | null {
        return DispGroupPointer.targetGroupName(this.dispGroupPtr);
    }

    setDispGroup(dispGroup: DispGroupT, coordSetId: number): void {
        DispGroupPointer.setDispGroup(
            this.dispGroupPtr,
            dispGroup,
            coordSetId,
            this.lookupService,
            this.branchTuple,
        );

        this.model.recompileModel();
        this.branchTuple.touchUndo();
    }
}
