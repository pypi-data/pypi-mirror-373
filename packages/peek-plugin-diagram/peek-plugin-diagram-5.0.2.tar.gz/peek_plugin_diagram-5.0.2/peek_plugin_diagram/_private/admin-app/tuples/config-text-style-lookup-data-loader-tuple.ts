
import { addTupleType, TupleDataLoaderTupleABC } from "@synerty/vortexjs";
import { FormControl, FormGroup, Validators } from "@angular/forms";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";
import { DispTextStyle } from "@peek/peek_plugin_diagram/_private/lookups";

@addTupleType
export class ConfigTextStyleLookupDataLoaderTuple extends TupleDataLoaderTupleABC {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigTextStyleLookupDataLoaderTuple";

    item: DispTextStyle;

    constructor() {
        super(ConfigTextStyleLookupDataLoaderTuple.tupleName);
    }

    override createFormGroup(): FormGroup | null {
        return new FormGroup({
            id: new FormControl(this.item.id),
            importHash: new FormControl(this.item.importHash),
            name: new FormControl(this.item.name, Validators.required),
            showForEdit: new FormControl(this.item.showForEdit),
            blockApiUpdate: new FormControl(this.item.blockApiUpdate),
            fontName: new FormControl(this.item.fontName, Validators.required),
            fontSize: new FormControl(this.item.fontSize),
            fontStyle: new FormControl(this.item.fontStyle),
            scalable: new FormControl(this.item.scalable),
            scaleFactor: new FormControl(this.item.scaleFactor),
            spacingBetweenTexts: new FormControl(this.item.spacingBetweenTexts),
            borderWidth: new FormControl(this.item.borderWidth),
            wrapTextAtChars: new FormControl(this.item.wrapTextAtChars),
            wrapTextAtCharSplitBetweenWords: new FormControl(
                this.item.wrapTextAtCharSplitBetweenWords
            ),
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