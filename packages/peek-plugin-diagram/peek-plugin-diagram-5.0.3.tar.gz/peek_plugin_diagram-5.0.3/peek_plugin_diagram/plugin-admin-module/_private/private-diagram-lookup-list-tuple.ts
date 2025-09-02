import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { DiagramLookupListTuple } from "../diagram-lookup-list-tuple";

@addTupleType
export class PrivateDiagramLookupListTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "PrivateDiagramLookupListTuple";

    id: number;
    key: string;
    name: string;

    data: { [key: string]: any } = {};

    constructor() {
        super(PrivateDiagramLookupListTuple.tupleName);
    }

    toExposedApiTuple(): DiagramLookupListTuple {
        const tuple = new DiagramLookupListTuple();
        tuple.key = this.key;
        tuple.name = this.name;
        tuple.data = this.data;
        return tuple;
    }
}
