
import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class ConfigLevelLookupListTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigLevelLookupListTuple";

    id: number;
    modelSetId: number;
    modelSetKey: string;
    canvasSetId: number;
    canvasSetKey: string;
    name: string;
    importHash: string;

    constructor() {
        super(ConfigLevelLookupListTuple.tupleName);
    }
}