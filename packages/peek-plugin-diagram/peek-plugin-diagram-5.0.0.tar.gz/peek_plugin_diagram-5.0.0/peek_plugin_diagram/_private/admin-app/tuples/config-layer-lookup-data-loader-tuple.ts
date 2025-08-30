import { addTupleType, TupleDataLoaderTupleABC } from "@synerty/vortexjs";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { DispLayer } from "@peek/peek_plugin_diagram/_private/lookups";

@addTupleType
export class ConfigLayerLookupDataLoaderTuple extends TupleDataLoaderTupleABC {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigLayerLookupDataLoaderTuple";

    item: DispLayer;

    constructor() {
        super(ConfigLayerLookupDataLoaderTuple.tupleName);
    }

    override createFormGroup(): FormGroup | null {
        return new FormGroup({
            id: new FormControl(this.item.id),
            parentId: new FormControl(this.item.parentId),
            importHash: new FormControl(this.item.importHash),
            name: new FormControl(this.item.name, Validators.required),
            showForEdit: new FormControl(this.item.showForEdit),
            blockApiUpdate: new FormControl(this.item.blockApiUpdate),
            order: new FormControl(this.item.order),
            selectable: new FormControl(this.item.selectable),
            visible: new FormControl(this.item.visible),
            editorVisible: new FormControl(this.item.editorVisible),
            editorEditable: new FormControl(this.item.editorEditable),
            opacity: new FormControl(this.item.opacity),
            // modelSetId: new FormControl(this.item.modelSetId),
        });
    }

    override updateValidation(formGroup: FormGroup): void {}

    override updateFromFormGroup(changes: {}): boolean | null {
        return TupleDataLoaderTupleABC.updateTupleFromFormGroup(
            changes,
            this.item,
        );
    }
}
