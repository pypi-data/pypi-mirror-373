import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import { LookupTypeE } from "@peek_admin/peek_plugin_diagram/diagram-edit-lookup-service";
import { NzModalService } from "ng-zorro-antd/modal";
import { ConfigEditorEditLookupColorModalComponent } from "../components/config-editor-edit-lookup-color-modal/config-editor-edit-lookup-color-modal.component";
import { ConfigEditorEditLookupLayerModalComponent } from "../components/config-editor-edit-lookup-layer-modal/config-editor-edit-lookup-layer-modal.component";
import { ConfigEditorEditLookupLevelModalComponent } from "../components/config-editor-edit-lookup-level-modal/config-editor-edit-lookup-level-modal.component";
import { ConfigEditorEditLookupLineStyleModalComponent } from "../components/config-editor-edit-lookup-line-style-modal/config-editor-edit-lookup-line-style-modal.component";
import { ConfigEditorEditLookupTextStyleModalComponent } from "../components/config-editor-edit-lookup-text-style-modal/config-editor-edit-lookup-text-style-modal.component";
import {
    ConfigObjectTypeE,
    CreatedLookupResultI,
    DiagramConfigStateService,
    NewLookupWithCoordSetI,
    NewLookupWithModelSetI,
} from "./diagram-config-state-service";
import { ConfigColorLookupListTuple } from "../tuples/config-color-lookup-list-tuple";
import { ConfigLayerLookupListTuple } from "../tuples/config-layer-lookup-list-tuple";
import { ConfigLevelLookupListTuple } from "../tuples/config-level-lookup-list-tuple";
import { ConfigLineStyleLookupListTuple } from "../tuples/config-line-style-lookup-list-tuple";
import { ConfigTextStyleLookupListTuple } from "../tuples/config-text-style-lookup-list-tuple";
import { firstValueFrom } from "rxjs";
import { DiagramTupleService } from "./diagram-tuple-service";
import { map } from "rxjs/operators";

@Injectable({
    providedIn: "root",
})
export class PrivateDiagramEditLookupModalService extends NgLifeCycleEvents {
    constructor(
        private nzModalService: NzModalService,
        private tupleService: DiagramTupleService,
    ) {
        super();
    }

    async showCreateModal(
        modelSetKey: string,
        coordSetKey: string,
        lookupType: LookupTypeE,
        name: string,
        importHash: string,
    ): Promise<CreatedLookupResultI> {
        // Implementation for creating a new lookup entry
        const modelSet = await this.tupleService.getModelSet(modelSetKey);
        const statService = new DiagramConfigStateService();

        let component: any | null;
        let title: string = "Create";
        let createObject:
            | NewLookupWithModelSetI
            | NewLookupWithCoordSetI
            | null = null;

        switch (lookupType) {
            case "color": {
                component = ConfigEditorEditLookupColorModalComponent;
                title = "Create Color Lookup";
                createObject = <NewLookupWithModelSetI>{
                    modelSetId: modelSet.id,
                    name: name,
                    importHash: importHash,
                };
                break;
            }
            case "layer": {
                component = ConfigEditorEditLookupLayerModalComponent;
                title = "Create Layer Lookup";
                createObject = <NewLookupWithModelSetI>{
                    modelSetId: modelSet.id,
                    name: name,
                    importHash: importHash,
                };
                break;
            }
            case "level": {
                const coordSet = await this.tupleService.getCoordSet(
                    modelSet.id,
                    coordSetKey,
                );
                component = ConfigEditorEditLookupLevelModalComponent;
                title = "Create Level Lookup";
                createObject = <NewLookupWithCoordSetI>{
                    coordSetId: coordSet.id,
                    name: name,
                    importHash: importHash,
                };
                break;
            }
            case "lineStyle": {
                component = ConfigEditorEditLookupLineStyleModalComponent;
                title = "Create Line Style Lookup";
                createObject = <NewLookupWithModelSetI>{
                    modelSetId: modelSet.id,
                    name: name,
                    importHash: importHash,
                };
                break;
            }
            case "textStyle": {
                component = ConfigEditorEditLookupTextStyleModalComponent;
                title = "Create Text Style Lookup";
                createObject = <NewLookupWithModelSetI>{
                    modelSetId: modelSet.id,
                    name: name,
                    importHash: importHash,
                };
                break;
            }
            default:
                throw new Error(`Unsupported lookup type: ${lookupType}`);
        }

        const modalRef = this.nzModalService.create({
            nzTitle: title,
            nzFooter: null,
            nzContent: component,
            nzData: {
                diagramConfigStateService: statService,
                createMode: createObject,
            },
            nzWidth: 720,
        });
        await firstValueFrom(modalRef.afterClose);
        return createObject.result;
    }

    async showEditModal(
        modelSetKey: string,
        coordSetKey: string,
        lookupType: LookupTypeE,
        lookupKeyId: { id?: number; key?: string },
    ): Promise<void> {
        const modelSet = await this.tupleService.getModelSet(modelSetKey);

        // Get the lookup using the extracted method
        const lookup = await this.getLookup(
            modelSetKey,
            modelSet.id,
            coordSetKey,
            lookupType,
            lookupKeyId,
        );

        const statService = new DiagramConfigStateService();

        // Determine the appropriate component based on lookup type
        let component: any | null = null;
        let objectType: ConfigObjectTypeE;
        let title;

        switch (lookupType) {
            case "color": {
                component = ConfigEditorEditLookupColorModalComponent;
                objectType = ConfigObjectTypeE.ColorLookup;
                title = "Color Lookup";
                break;
            }
            case "layer": {
                component = ConfigEditorEditLookupLayerModalComponent;
                objectType = ConfigObjectTypeE.LayerLookup;
                title = "Layer Lookup";
                break;
            }
            case "level": {
                component = ConfigEditorEditLookupLevelModalComponent;
                objectType = ConfigObjectTypeE.LevelLookup;
                title = "Level Lookup";
                break;
            }
            case "lineStyle": {
                component = ConfigEditorEditLookupLineStyleModalComponent;
                objectType = ConfigObjectTypeE.LineStyleLookup;
                title = "Line Style Lookup";
                break;
            }
            case "textStyle": {
                component = ConfigEditorEditLookupTextStyleModalComponent;
                objectType = ConfigObjectTypeE.TextStyleLookup;
                title = "Text Style Lookup";
                break;
            }
            default:
                throw new Error(`Unsupported lookup type: ${lookupType}`);
        }

        statService.selectConfigObject(objectType, lookup.id);

        this.nzModalService.create({
            nzTitle: title,
            nzFooter: null,
            nzContent: component,
            nzData: {
                diagramConfigStateService: statService,
                createMode: null,
            },
            nzWidth: 720,
            nzMaskClosable: false,
        });
    }

    /**
     * Gets a lookup object based on provided parameters
     *
     * @param modelSetKey
     * @param modelSetId The ID of the model set
     * @param coordSetKey The coordinate set key
     * @param lookupType The type of lookup to retrieve
     * @param lookupKeyId The key/importHash of the lookup
     * @returns The lookup object, or null if not found
     */
    private async getLookup(
        modelSetKey: string,
        modelSetId: number,
        coordSetKey: string,
        lookupType: LookupTypeE,
        lookupKeyId: { id?: number; key?: string },
    ): Promise<any> {
        let ts: TupleSelector | null = null;

        switch (lookupType) {
            case "color": {
                ts = new TupleSelector(ConfigColorLookupListTuple.tupleName, {
                    modelSetId: modelSetId,
                });
                break;
            }

            case "layer": {
                ts = new TupleSelector(ConfigLayerLookupListTuple.tupleName, {
                    modelSetId: modelSetId,
                });
                break;
            }

            case "level": {
                const coordSet = await this.tupleService.getCoordSet(
                    modelSetId,
                    coordSetKey,
                );
                ts = new TupleSelector(ConfigLevelLookupListTuple.tupleName, {
                    canvasId: coordSet.id,
                });
                break;
            }

            case "lineStyle": {
                ts = new TupleSelector(
                    ConfigLineStyleLookupListTuple.tupleName,
                    {
                        modelSetId: modelSetId,
                    },
                );
                break;
            }

            case "textStyle": {
                ts = new TupleSelector(
                    ConfigTextStyleLookupListTuple.tupleName,
                    {
                        modelSetId: modelSetId,
                    },
                );
                break;
            }
        }

        const lookups = await firstValueFrom(
            this.tupleService.observer
                .subscribeToTupleSelector(ts)
                .pipe(map((tuples: Tuple[]) => tuples as any[])),
        );

        const lookup = lookups.find((lu) =>
            lookupKeyId.key
                ? lu.importHash == lookupKeyId.key
                : lu.id == lookupKeyId.id,
        );

        if (lookup == null) {
            throw new Error(
                `modelSetKey=${modelSetKey}` +
                    ` coordSetKey=${coordSetKey}` +
                    ` lookupType=${lookupType}` +
                    ` key/importHash ${lookup} not found`,
            );
        }

        return lookup;
    }
}
