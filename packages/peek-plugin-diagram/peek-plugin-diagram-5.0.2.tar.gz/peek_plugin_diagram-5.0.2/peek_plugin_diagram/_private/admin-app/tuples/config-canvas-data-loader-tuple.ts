import { addTupleType, TupleDataLoaderTupleABC } from "@synerty/vortexjs";
import { FormArray, FormControl, FormGroup, Validators } from "@angular/forms";
import {
    ModelCoordSet,
    ModelCoordSetGridSize,
} from "@peek/peek_plugin_diagram/_private/tuples";
import { diagramTuplePrefix } from "@peek/peek_plugin_diagram/_private";

@addTupleType
export class ConfigCanvasDataLoaderTuple extends TupleDataLoaderTupleABC {
    public static readonly tupleName =
        diagramTuplePrefix + "ConfigCanvasDataLoaderTuple";

    item: ModelCoordSet = new ModelCoordSet();

    // These are for info only
    modelSetKey: string;
    coordSetKey: string;

    constructor() {
        super(ConfigCanvasDataLoaderTuple.tupleName);
    }

    static createGridSizeFormGroup(gridSize: ModelCoordSetGridSize): FormGroup {
        return new FormGroup({
            id: new FormControl(gridSize.id),
            coordSetId: new FormControl(gridSize.coordSetId),
            key: new FormControl(gridSize.key, Validators.required),
            min: new FormControl(gridSize.min, Validators.required),
            max: new FormControl(gridSize.max, Validators.required),
            xGrid: new FormControl(gridSize.xGrid, Validators.required),
            yGrid: new FormControl(gridSize.yGrid, Validators.required),
            smallestTextSize: new FormControl(
                gridSize.smallestTextSize,
                Validators.required,
            ),
            smallestShapeSize: new FormControl(
                gridSize.smallestShapeSize,
                Validators.required,
            ),
        });
    }

    override createFormGroup(): FormGroup | null {
        const gridSizeControls: FormGroup[] = [];
        for (const gridSize of this.item.gridSizes) {
            gridSizeControls.push(
                ConfigCanvasDataLoaderTuple.createGridSizeFormGroup(gridSize),
            );
        }

        return new FormGroup({
            id: new FormControl(this.item.id),
            key: new FormControl(this.item.key, Validators.required),
            name: new FormControl(this.item.name, Validators.required),
            initialPanX: new FormControl(this.item.initialPanX),
            initialPanY: new FormControl(this.item.initialPanY),
            initialZoom: new FormControl(this.item.initialZoom),
            initialDarkMode: new FormControl(this.item.initialDarkMode),
            positionOnZoom: new FormControl(this.item.positionOnZoom),
            backgroundDarkColor: new FormControl(this.item.backgroundDarkColor),
            backgroundLightColor: new FormControl(
                this.item.backgroundLightColor,
            ),
            enabled: new FormControl(this.item.enabled),
            lightModeEnabled: new FormControl(this.item.lightModeEnabled),
            comment: new FormControl(this.item.comment),
            modelSetId: new FormControl(this.item.modelSetId),
            minZoom: new FormControl(this.item.minZoom),
            maxZoom: new FormControl(this.item.maxZoom),
            gridSizes: new FormArray(gridSizeControls),
            data: new FormControl(this.item.data),
            dispGroupTemplatesEnabled: new FormControl(
                this.item.dispGroupTemplatesEnabled,
            ),
            edgeTemplatesEnabled: new FormControl(
                this.item.edgeTemplatesEnabled,
            ),
            branchesEnabled: new FormControl(this.item.branchesEnabled),
            editEnabled: new FormControl(this.item.editEnabled),
            editDefaultLayerId: new FormControl(this.item.editDefaultLayerId),
            editDefaultLevelId: new FormControl(this.item.editDefaultLevelId),
            editDefaultColorId: new FormControl(this.item.editDefaultColorId),
            editDefaultLineStyleId: new FormControl(
                this.item.editDefaultLineStyleId,
            ),
            editDefaultTextStyleId: new FormControl(
                this.item.editDefaultTextStyleId,
            ),
            editDefaultVertexCoordSetId: new FormControl(
                this.item.editDefaultVertexCoordSetId,
            ),
            editDefaultVertexGroupName: new FormControl(
                this.item.editDefaultVertexGroupName,
            ),
            editDefaultEdgeCoordSetId: new FormControl(
                this.item.editDefaultEdgeCoordSetId,
            ),
            editDefaultEdgeGroupName: new FormControl(
                this.item.editDefaultEdgeGroupName,
            ),
            userGroupsAllowed: new FormControl(this.item.userGroupsAllowed),
            userGroupsDenied: new FormControl(this.item.userGroupsDenied),
            order: new FormControl(this.item.order),
        });
    }

    override updateValidation(formGroup: FormGroup): void {}

    override updateFromFormGroup(changes: {}): boolean | null {
        return TupleDataLoaderTupleABC.updateTupleFromFormGroup(
            changes,
            this.item,
            { gridSizes: ModelCoordSetGridSize },
        );
    }
}
