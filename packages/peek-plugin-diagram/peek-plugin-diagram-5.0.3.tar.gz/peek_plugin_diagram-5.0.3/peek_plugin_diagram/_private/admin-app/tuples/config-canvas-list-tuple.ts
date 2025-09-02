import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private/PluginNames";

@addTupleType
export class ConfigCanvasListTuple extends Tuple {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigCanvasListTuple";

    id: number;
    key: string;
    modelSetId: number;
    modelSetKey: string;
    name: string;
    enabled: boolean;
    dispGroupTemplatesEnabled: boolean;
    edgeTemplatesEnabled: boolean;

    constructor() {
        super(ConfigCanvasListTuple.tupleName);
    }

    get nameKey(): string {
        return `${this.name} (${this.key})`;
    }
}
