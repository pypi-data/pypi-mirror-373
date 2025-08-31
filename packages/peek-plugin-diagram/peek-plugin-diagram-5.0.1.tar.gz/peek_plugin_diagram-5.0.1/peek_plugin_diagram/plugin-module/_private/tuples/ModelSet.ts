import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "../PluginNames";

@addTupleType
export class ModelSet extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "ModelSet";

    id: number;
    key: string;
    name: string;
    comment: string;

    constructor() {
        super(ModelSet.tupleName);
    }
}
