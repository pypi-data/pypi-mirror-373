
import { addTupleType, TupleDataLoaderTupleABC } from "@synerty/vortexjs";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { DispLineStyle } from "@peek/peek_plugin_diagram/_private/lookups";

@addTupleType
export class ConfigLineStyleLookupDataLoaderTuple extends TupleDataLoaderTupleABC {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigLineStyleLookupDataLoaderTuple";

    item: DispLineStyle;

    constructor() {
        super(ConfigLineStyleLookupDataLoaderTuple.tupleName);
    }

    override createFormGroup(): FormGroup | null {
        return new FormGroup({
            id: new FormControl(this.item.id),
            importHash: new FormControl(this.item.importHash),
            name: new FormControl(this.item.name, Validators.required),
            showForEdit: new FormControl(this.item.showForEdit),
            blockApiUpdate: new FormControl(this.item.blockApiUpdate),
            backgroundFillDashSpace: new FormControl(this.item.backgroundFillDashSpace),
            capStyle: new FormControl(this.item.capStyle),
            joinStyle: new FormControl(this.item.joinStyle),
            dashPattern: new FormControl(this.item.dashPattern),
            startArrowSize: new FormControl(this.item.startArrowSize),
            endArrowSize: new FormControl(this.item.endArrowSize),
            scalable: new FormControl(this.item.scalable),
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