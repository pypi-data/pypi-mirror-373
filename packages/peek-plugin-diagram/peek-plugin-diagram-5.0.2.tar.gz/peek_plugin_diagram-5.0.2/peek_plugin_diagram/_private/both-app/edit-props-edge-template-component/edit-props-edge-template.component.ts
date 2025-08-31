import { Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents, Payload, TupleSelector } from "@synerty/vortexjs";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples/ModelCoordSet";
import { GroupDispsTuple } from "@peek/peek_plugin_diagram/_private/tuples/GroupDispsTuple";
import { PrivateDiagramTupleService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramTupleService";
import { GridTuple } from "@peek/peek_plugin_diagram/_private/grid-loader/GridTuple";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { LinkedGrid } from "../cache/LinkedGrid.web";
import {
    DispEdgeTemplate,
    DispEdgeTemplateT,
} from "../canvas-shapes/DispEdgeTemplate";
import { PeekCanvasEdgeTemplatePropsContext } from "../canvas/PeekCanvasEdgeTemplatePropsContext";
import { DispGroup } from "../canvas-shapes/DispGroup";

@Component({
    selector: "pl-diagram-edit-props-edge-template",
    templateUrl: "edit-props-edge-template.component.html",
    styleUrls: ["edit-props-edge-template.component.scss"],
})
export class EditPropsEdgeTemplateComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;

    context: PeekCanvasEdgeTemplatePropsContext;
    templateCoordSets: ModelCoordSet[] = [];
    selectedCoordSetId: number = null;
    edgeTemplates: DispEdgeTemplateT[] = [];
    selectedEdgeTemplate = null;
    coordSet: ModelCoordSet = new ModelCoordSet();

    private coordSetCache: PrivateDiagramCoordSetService;
    private unsubSubject = new Subject<void>();

    constructor(
        private tupleService: PrivateDiagramTupleService,
        abstractCoordSetCache: DiagramCoordSetService,
        private lookupService: PrivateDiagramLookupService,
    ) {
        super();

        this.coordSetCache = <PrivateDiagramCoordSetService>(
            abstractCoordSetCache
        );
    }

    override ngOnInit() {
        this.templateCoordSets = [];

        let coordSets = this.coordSetCache.coordSets(
            this.canvasEditor.branchContext.modelSetKey,
        );

        for (let coordSet of coordSets) {
            if (coordSet.id === this.canvasEditor.coordSetId) {
                this.coordSet = coordSet;
                break;
            }
        }

        for (let coordSet of coordSets) {
            if (coordSet.edgeTemplatesEnabled === true)
                this.templateCoordSets.push(coordSet);
        }

        this.templateCoordSets = this.templateCoordSets.sort((a, b) =>
            a.name.localeCompare(b.name),
        );

        this.context = this.canvasEditor.props.edgeTemplatePanelContext;
        this.canvasEditor.props.edgeTemplatePanelContextObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((context: PeekCanvasEdgeTemplatePropsContext) => {
                this.edgeTemplates = [];
                this.selectedEdgeTemplate = null;
                this.selectedCoordSetId = null;
                this.context = context;
                this.initSelectedCoordSetId();
            });
        this.initSelectedCoordSetId();
    }

    noedgeTemplates(): boolean {
        return this.edgeTemplates.length == 0;
    }

    isSelectedEdgeTemplate(item: DispEdgeTemplateT): boolean {
        return (
            this.selectedEdgeTemplate != null &&
            item.id == this.selectedEdgeTemplate.id
        );
    }

    selectedCoordSetIdChanged(coordSetId: number): void {
        this.selectedCoordSetId = coordSetId;

        let tupleSelector = new TupleSelector(GroupDispsTuple.tupleName, {
            coordSetId: coordSetId,
        });

        this.unsubSubject.next();

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(tupleSelector)
            .pipe(takeUntil(this.unsubSubject))
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: GroupDispsTuple[]) => {
                if (tuples.length == 0) return;

                let gridDispTuple = tuples[0];

                if (gridDispTuple.encodedGridTuple == null) return;

                Payload.fromEncodedPayload(gridDispTuple.encodedGridTuple)
                    .then((payload: Payload) => {
                        let gridTuple: GridTuple = payload.tuples[0];
                        let linkedGrid = new LinkedGrid(
                            gridTuple,
                            this.lookupService,
                        );
                        this.edgeTemplates = linkedGrid.disps.sort((a, b) =>
                            DispGroup.groupName(a).localeCompare(
                                DispGroup.groupName(b),
                            ),
                        );
                        this.initSelectedEdgeTemplate();
                    })
                    .catch((err) => {
                        console.log(
                            `GridLoader.emitEncodedGridTuples decode error: ${err}`,
                        );
                    });
            });
    }

    dispName(disp: DispEdgeTemplateT): string {
        return DispEdgeTemplate.templateName(disp);
    }

    toggleEnabled(disp: DispEdgeTemplateT): void {
        this.selectedEdgeTemplate = disp;
        this.context.setEdgeTemplate(
            this.selectedEdgeTemplate,
            this.selectedCoordSetId,
        );
    }

    private initSelectedCoordSetId(): void {
        if (this.context == null) return;

        let coordSetId = this.context.targetEdgeTemplateCoordSetId;

        if (coordSetId != null) {
            this.selectedCoordSetId = coordSetId;
            this.selectedCoordSetIdChanged(this.selectedCoordSetId);
        } else if (this.coordSet.editDefaultEdgeCoordSetId != null) {
            this.selectedCoordSetId = this.coordSet.editDefaultEdgeCoordSetId;
            this.selectedCoordSetIdChanged(this.selectedCoordSetId);
        } else if (this.templateCoordSets.length != 0) {
            this.selectedCoordSetId = this.templateCoordSets[0].id;
            this.selectedCoordSetIdChanged(this.selectedCoordSetId);
        }
    }

    private initSelectedEdgeTemplate(): void {
        if (this.context == null) return;

        let setName = (name) => {
            for (let edgeTemplate of this.edgeTemplates) {
                if (DispEdgeTemplate.templateName(edgeTemplate) == name) {
                    this.selectedEdgeTemplate = edgeTemplate;
                    break;
                }
            }
        };

        const name = this.context.targetEdgeTemplateName;

        if (name != null) setName(name);
        else if (this.coordSet.editDefaultEdgeGroupName != null)
            setName(this.coordSet.editDefaultEdgeGroupName);
    }
}
