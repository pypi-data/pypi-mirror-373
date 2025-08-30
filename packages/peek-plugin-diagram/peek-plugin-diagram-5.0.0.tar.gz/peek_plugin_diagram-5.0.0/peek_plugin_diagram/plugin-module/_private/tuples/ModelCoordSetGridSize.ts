import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class ModelCoordSetGridSize extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ModelCoordSetGridSize";

    id: number;
    coordSetId: number;
    key: number;
    min: number;
    max: number;
    xGrid: number;
    yGrid: number;

    smallestTextSize: number;
    smallestShapeSize: number;

    constructor() {
        super(ModelCoordSetGridSize.tupleName);
    }
}
