import { Injectable } from "@angular/core";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";

// noinspection TypeScriptCheckImport
import { PrivateDiagramEditLookupModalService } from "@_peek/peek_plugin_diagram/services/private-diagram-edit-lookup-modal-service";
import { Observable } from "rxjs";
import { PrivateDiagramTupleService } from "@peek/peek_plugin_diagram/_private/services";
import { DiagramLookupListTuple } from "@peek_admin/peek_plugin_diagram/diagram-lookup-list-tuple";
import { PrivateDiagramLookupListTuple } from "@peek_admin/peek_plugin_diagram/_private/private-diagram-lookup-list-tuple";
import { map } from "rxjs/operators";

export enum LookupTypeE {
    LEVEL = "level",
    LAYER = "layer",
    COLOR = "color",
    LINE_STYLE = "lineStyle",
    TEXT_STYLE = "textStyle",
}

@Injectable({ providedIn: "root" })
export class DiagramEditLookupService extends NgLifeCycleEvents {
    constructor(
        private lookupModalService: PrivateDiagramEditLookupModalService,
        private tupleService: PrivateDiagramTupleService,
    ) {
        super();
    }

    async editLookup(
        modelSetKey: string,
        coordSetKey: string | null,
        lookupType: LookupTypeE,
        lookupKey: string,
    ): Promise<void> {
        await this.lookupModalService.showEditModal(
            modelSetKey,
            coordSetKey,
            lookupType,
            { key: lookupKey },
        );
    }

    async createLookup(
        modelSetKey: string,
        coordSetKey: string | null,
        lookupType: LookupTypeE,
        name: string,
        importHash: string,
    ): Promise<string> {
        const result = await this.lookupModalService.showCreateModal(
            modelSetKey,
            coordSetKey,
            lookupType,
            name,
            importHash,
        );
        return result.importHash;
    }

    lookupListItems(
        modelSetKey: string,
        coordSetKey: string | null,
        lookupType: LookupTypeE,
    ): Observable<DiagramLookupListTuple[]> {
        return this.tupleService.observer
            .subscribeToTupleSelector(
                new TupleSelector(PrivateDiagramLookupListTuple.tupleName, {
                    lookupType: lookupType,
                    modelSetKey: modelSetKey,
                    coordSetKey:
                        lookupType == LookupTypeE.LEVEL ? coordSetKey : null,
                }),
            )
            .pipe(
                map((tuples) =>
                    tuples.map((t) =>
                        (
                            t as PrivateDiagramLookupListTuple
                        ).toExposedApiTuple(),
                    ),
                ),
            ) as Observable<DiagramLookupListTuple[]>;
    }
}
