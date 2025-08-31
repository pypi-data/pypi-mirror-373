import { addTupleType, Tuple, TupleActionABC } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class TriggerCanvasShapeCompileResultTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "TriggerCanvasShapeCompileResultTuple";

    shapesQueued: number;
    gridsDeleted: number;

    constructor() {
        super(TriggerCanvasShapeCompileResultTuple.tupleName);
    }
}
