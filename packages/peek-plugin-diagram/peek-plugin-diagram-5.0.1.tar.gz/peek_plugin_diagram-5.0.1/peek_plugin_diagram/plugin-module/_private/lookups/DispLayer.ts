import { addTupleType, Tuple } from "@synerty/vortexjs";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { ShapeLayerTuple } from "@peek/peek_plugin_diagram/lookup_tuples";

@addTupleType
export class DispLayer extends Tuple {
    public static readonly tupleName = diagramTuplePrefix + "DispLayer";

    // Tuple Fields
    key: string;
    modelSetKey: string;

    id: number;
    parentId: number | null;
    parentKey: string | null;

    modelSetId: number;

    name: string;

    importHash: string;
    showForEdit: boolean;
    blockApiUpdate: boolean;

    order: number;
    selectable: boolean | null;
    visible: boolean | null;
    editorVisible: boolean;
    editorEditable: boolean;
    opacity: number;

    // Default values - underscore prevents serialization
    private _defaultVisible: boolean | null = null;
    private _defaultsInitialised: boolean = false;

    // Parent/Child relationships - underscore prevents serialization
    private _parentLayer: DispLayer | null = null;
    private _childLayers: DispLayer[] = [];

    constructor() {
        super(DispLayer.tupleName);
    }

    get parentLayer(): DispLayer | null {
        return this._parentLayer;
    }

    set parentLayer(value: DispLayer | null) {
        this._parentLayer = value;
    }

    get childLayers(): DispLayer[] {
        return this._childLayers;
    }

    get childLayerSortedByName(): DispLayer[] {
        return this._childLayers.sort((o1, o2) =>
            o1.name.localeCompare(o2.name),
        );
    }

    get hasChildren(): boolean {
        return this._childLayers.length !== 0;
    }

    set childLayers(value: DispLayer[]) {
        this._childLayers = value;
    }

    initialiseDefaults(): void {
        if (this._defaultsInitialised) {
            return;
        }

        this._defaultVisible = this.visible;
        this._defaultsInitialised = true;
    }

    resetToDefaultVisible(): void {
        this.visible = this._defaultVisible;
    }

    calculateEffectiveVisibility(): boolean {
        if (this.visible != null) {
            return this.visible;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveVisibility();
        }

        return true;
    }

    calculateEffectiveEditorVisibility(): boolean {
        if (this.editorVisible != null) {
            return this.editorVisible;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveEditorVisibility();
        }

        return true;
    }

    calculateEffectiveSelectability(): boolean {
        if (this.selectable != null) {
            return this.selectable;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveSelectability();
        }

        return true;
    }

    calculateEffectiveEditorEditable(): boolean {
        if (this.editorEditable != null) {
            return this.editorEditable;
        }

        if (this.parentLayer) {
            return this.parentLayer.calculateEffectiveEditorEditable();
        }

        return true;
    }

    toTuple(): ShapeLayerTuple {
        const tuple_ = new ShapeLayerTuple();
        tuple_.key = this.key;
        tuple_.modelSetKey = this.modelSetKey;

        tuple_.name = this.name;
        tuple_.showForEdit = this.showForEdit;

        tuple_.order = this.order;
        tuple_.selectable = this.selectable;
        tuple_.visible = this.visible;
        tuple_.opacity = this.opacity;
        tuple_.editorVisible = this.editorVisible;
        tuple_.editorEditable = this.editorEditable;
        tuple_.parentKey = this.parentKey;

        return tuple_;
    }
}
