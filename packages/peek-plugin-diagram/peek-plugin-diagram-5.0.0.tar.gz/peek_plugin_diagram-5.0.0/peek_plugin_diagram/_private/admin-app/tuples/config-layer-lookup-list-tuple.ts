import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class ConfigLayerLookupListTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigLayerLookupListTuple";

    id: number;
    modelSetId: number;
    modelSetKey: string;
    name: string;
    importHash: string;
    parentId: number;

    constructor() {
        super(ConfigLayerLookupListTuple.tupleName);
    }
}
