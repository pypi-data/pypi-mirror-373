
import { addTupleType, TupleDataLoaderTupleABC } from "@synerty/vortexjs";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { DispLevel } from "@peek/peek_plugin_diagram/_private/lookups";

@addTupleType
export class ConfigLevelLookupDataLoaderTuple extends TupleDataLoaderTupleABC {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigLevelLookupDataLoaderTuple";

    item: DispLevel;

    constructor() {
        super(ConfigLevelLookupDataLoaderTuple.tupleName);
    }

    override createFormGroup(): FormGroup | null {
        return new FormGroup({
            id: new FormControl(this.item.id),
            importHash: new FormControl(this.item.importHash),
            name: new FormControl(this.item.name, Validators.required),
            showForEdit: new FormControl(this.item.showForEdit),
            blockApiUpdate: new FormControl(this.item.blockApiUpdate),
            order: new FormControl(this.item.order),
            minZoom: new FormControl(this.item.minZoom),
            maxZoom: new FormControl(this.item.maxZoom),
            // coordSetId: new FormControl(this.item.coordSetId),
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