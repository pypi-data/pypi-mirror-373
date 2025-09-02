import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class ShapeGroupListItemTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ShapeGroupListItemTuple";

    name: string;

    constructor() {
        super(ShapeGroupListItemTuple.tupleName);
    }
}
