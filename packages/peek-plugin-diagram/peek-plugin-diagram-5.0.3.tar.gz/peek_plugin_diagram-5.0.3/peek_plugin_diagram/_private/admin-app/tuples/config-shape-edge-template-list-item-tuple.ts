import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class ShapeEdgeTemplateListItemTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ShapeEdgeListItemTuple";

    name: string;

    constructor() {
        super(ShapeEdgeTemplateListItemTuple.tupleName);
    }
}
