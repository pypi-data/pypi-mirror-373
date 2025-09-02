import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class ConfigModelSetListTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigModelListTuple";

    id: number;
    key: string;
    name: string;

    constructor() {
        super(ConfigModelSetListTuple.tupleName);
    }
}
