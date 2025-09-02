import { addTupleType, TupleDataLoaderTupleABC } from "@synerty/vortexjs";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { DispColor } from "@peek/peek_plugin_diagram/_private/lookups";

@addTupleType
export class ConfigColorLookupDataLoaderTuple extends TupleDataLoaderTupleABC {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigColorLookupDataLoaderTuple";

    item: DispColor;

    constructor() {
        super(ConfigColorLookupDataLoaderTuple.tupleName);
    }

    override createFormGroup(): FormGroup | null {
        return new FormGroup({
            id: new FormControl(this.item.id),
            importHash: new FormControl(this.item.importHash),
            name: new FormControl(this.item.name, Validators.required),
            showForEdit: new FormControl(this.item.showForEdit),
            blockApiUpdate: new FormControl(this.item.blockApiUpdate),
            darkColor: new FormControl(this.item.darkColor),
            lightColor: new FormControl(this.item.lightColor),
            darkFillBase64Image: new FormControl(this.item.darkFillBase64Image),
            lightFillBase64Image: new FormControl(
                this.item.lightFillBase64Image,
            ),
            altColor: new FormControl(this.item.altColor),
            swapPeriod: new FormControl(this.item.swapPeriod),
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
