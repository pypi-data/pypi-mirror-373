import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class TriggerCanvasShapeCompileTupleAction extends TupleActionABC {
    public static readonly tupleName =
        diagramTuplePrefix + "TriggerCanvasShapeCompileTupleAction";

    canvasId: number;

    constructor() {
        super(TriggerCanvasShapeCompileTupleAction.tupleName);
    }
}
