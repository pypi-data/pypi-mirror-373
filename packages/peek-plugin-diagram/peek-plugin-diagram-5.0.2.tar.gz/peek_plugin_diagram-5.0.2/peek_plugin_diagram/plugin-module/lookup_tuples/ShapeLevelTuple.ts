import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class ShapeLevelTuple extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "ShapeLevelTuple";

    key: string;
    modelSetKey: string;
    coordSetKey: string;
    name: string;
    order: number;
    minZoom: number;
    maxZoom: number;
    showForEdit: boolean;

    constructor() {
        super(ShapeLevelTuple.tupleName);
    }

    isVisibleAtZoom(zoom: number): boolean {
        return this.minZoom <= zoom && zoom < this.maxZoom;
    }
}
