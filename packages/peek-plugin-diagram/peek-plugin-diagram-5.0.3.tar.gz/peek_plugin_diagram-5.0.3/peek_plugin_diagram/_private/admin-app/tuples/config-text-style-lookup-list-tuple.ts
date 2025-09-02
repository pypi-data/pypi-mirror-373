
import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class ConfigTextStyleLookupListTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigTextStyleLookupListTuple";

    id: number;
    modelSetId: number;
    modelSetKey: string;
    name: string;
    importHash: string;

    constructor() {
        super(ConfigTextStyleLookupListTuple.tupleName);
    }
}