import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class ShapeLayerTuple extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "ShapeLayerTuple";

    key: string;
    parentKey: string | null;
    modelSetKey: string;
    name: string;
    order: number;
    selectable: boolean | null;
    visible: boolean | null;
    editorVisible: boolean;
    editorEditable: boolean;
    opacity: number;
    showForEdit: boolean;

    // Parent/Child relationships - underscore prevents serialization
    private _parentLayer: ShapeLayerTuple | null = null;
    private _childLayers: ShapeLayerTuple[] = [];

    constructor() {
        super(ShapeLayerTuple.tupleName);
    }

    get parentLayer(): ShapeLayerTuple | null {
        return this._parentLayer;
    }

    set parentLayer(value: ShapeLayerTuple | null) {
        this._parentLayer = value;
    }

    get childLayers(): ShapeLayerTuple[] {
        return this._childLayers;
    }

    set childLayers(value: ShapeLayerTuple[]) {
        this._childLayers = value;
    }

    calculateEffectiveVisibility(): boolean {
        if (this.visible !== null) {
            return this.visible;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveVisibility();
        }

        return true;
    }

    calculateEffectiveEditorVisibility(): boolean {
        if (this.editorVisible !== null && this.editorVisible !== undefined) {
            return this.editorVisible;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveEditorVisibility();
        }

        return true;
    }

    calculateEffectiveSelectability(): boolean {
        if (this.selectable !== null) {
            return this.selectable;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveSelectability();
        }

        return true;
    }

    calculateEffectiveEditorEditable(): boolean {
        if (this.editorEditable !== null && this.editorEditable !== undefined) {
            return this.editorEditable;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveEditorEditable();
        }

        return true;
    }
}