import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class DiagramLookupListTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "DiagramLookupListTuple";

    key: string;
    name: string;

    data: { [key: string]: any } = {};

    constructor() {
        super(DiagramLookupListTuple.tupleName);
    }
}
