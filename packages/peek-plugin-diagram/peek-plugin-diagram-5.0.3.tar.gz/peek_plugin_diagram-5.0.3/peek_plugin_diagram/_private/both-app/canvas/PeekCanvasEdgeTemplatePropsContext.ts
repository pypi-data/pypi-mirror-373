import { DispPolyline, DispPolylineT } from "../canvas-shapes/DispPolyline";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch/BranchTuple";
import { PeekCanvasModel } from "./PeekCanvasModel.web";
import { DispEdgeTemplateT } from "../canvas-shapes/DispEdgeTemplate";

export class PeekCanvasEdgeTemplatePropsContext {
    constructor(
        private model: PeekCanvasModel,
        private polyline: DispPolylineT,
        private lookupService: PrivateDiagramLookupService,
        private branchTuple: BranchTuple,
    ) {}

    get targetEdgeTemplateCoordSetId(): number | null {
        return DispPolyline.targetEdgeTemplateCoordSetId(this.polyline);
    }

    get targetEdgeTemplateName(): string | null {
        return DispPolyline.targetEdgeTemplateName(this.polyline);
    }

    setEdgeTemplate(edgeTemplate: DispEdgeTemplateT, coordSetId: number): void {
        DispPolyline.setEdgeTemplate(
            this.polyline,
            edgeTemplate,
            coordSetId,
            this.lookupService,
            this.branchTuple,
        );

        this.branchTuple.touchUndo();
        this.model.recompileModel();
    }
}
