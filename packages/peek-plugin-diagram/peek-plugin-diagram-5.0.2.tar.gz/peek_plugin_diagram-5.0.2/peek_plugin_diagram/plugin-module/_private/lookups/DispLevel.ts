import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import {
    ShapeLayerTuple,
    ShapeLevelTuple,
} from "@peek/peek_plugin_diagram/lookup_tuples";

@addTupleType
export class DispLevel extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispLevel";

    // Tuple Fields
    key: string;
    modelSetKey: string;
    coordSetKey: string;

    id: number;
    name: string;

    importHash: string;
    showForEdit: boolean;
    blockApiUpdate: boolean;

    order: number;
    minZoom: number;
    maxZoom: number;
    coordSetId: number;

    constructor() {
        super(DispLevel.tupleName);
    }

    isVisibleAtZoom(zoom: number): boolean {
        return this.minZoom <= zoom && zoom < this.maxZoom;
    }

    toTuple(): ShapeLevelTuple {
        const tuple_ = new ShapeLevelTuple();
        tuple_.key = this.key;
        tuple_.modelSetKey = this.modelSetKey;
        tuple_.coordSetKey = this.coordSetKey;

        tuple_.name = this.name;
        tuple_.showForEdit = this.showForEdit;

        tuple_.order = this.order;
        tuple_.minZoom = this.minZoom;
        tuple_.maxZoom = this.maxZoom;

        return tuple_;
    }
}
