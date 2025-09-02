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
import { PrivateDiagramGridLoaderServiceA } from "@peek/peek_plugin_diagram/_private/grid-loader/PrivateDiagramGridLoaderServiceA";
import { GridTuple } from "@peek/peek_plugin_diagram/_private/grid-loader/GridTuple";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { LinkedGrid } from "../cache/LinkedGrid.web";
import { DispGroup, DispGroupT } from "../canvas-shapes/DispGroup";
import { PeekCanvasGroupPtrPropsContext } from "../canvas/PeekCanvasGroupPtrPropsContext";

@Component({
    selector: "pl-diagram-edit-props-group-ptr",
    templateUrl: "edit-props-group-ptr.component.html",
    styleUrls: ["edit-props-group-ptr.component.scss"],
})
export class EditPropsGroupPtrComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;

    context: PeekCanvasGroupPtrPropsContext;
    templateCoordSets: ModelCoordSet[] = [];
    selectedCoordSetId: number = null;
    dispGroups: DispGroupT[] = [];
    selectedDispGroup = null;
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
            if (coordSet.dispGroupTemplatesEnabled === true)
                this.templateCoordSets.push(coordSet);
        }

        this.templateCoordSets = this.templateCoordSets.sort((a, b) =>
            a.name.localeCompare(b.name),
        );

        this.context = this.canvasEditor.props.groupPtrPanelContext;
        this.canvasEditor.props.groupPtrPanelContextObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((context: PeekCanvasGroupPtrPropsContext) => {
                this.dispGroups = [];
                this.selectedDispGroup = null;
                this.selectedCoordSetId = null;
                this.context = context;
                this.initSelectedCoordSetId();
            });
        this.initSelectedCoordSetId();
    }

    noDispGroups(): boolean {
        return this.dispGroups.length == 0;
    }

    isSelectedDispGroup(item: DispGroupT): boolean {
        return (
            this.selectedDispGroup != null &&
            item.id == this.selectedDispGroup.id
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
                        this.dispGroups = linkedGrid.disps.sort((a, b) =>
                            DispGroup.groupName(a).localeCompare(
                                DispGroup.groupName(b),
                            ),
                        );
                        this.initSelectedDispGroup();
                    })
                    .catch((err) => {
                        console.log(
                            `GridLoader.emitEncodedGridTuples decode error: ${err}`,
                        );
                    });
            });
    }

    dispName(disp: DispGroupT): string {
        return DispGroup.groupName(disp);
    }

    toggleEnabled(disp: DispGroupT): void {
        this.selectedDispGroup = disp;
        this.context.setDispGroup(
            this.selectedDispGroup,
            this.selectedCoordSetId,
        );
    }

    private initSelectedCoordSetId(): void {
        if (this.context == null) return;

        let coordSetId = this.context.targetDispGroupCoordSetId;

        if (coordSetId != null) {
            this.selectedCoordSetId = coordSetId;
            this.selectedCoordSetIdChanged(this.selectedCoordSetId);
        } else if (this.coordSet.editDefaultVertexCoordSetId != null) {
            this.selectedCoordSetId = this.coordSet.editDefaultVertexCoordSetId;
            this.selectedCoordSetIdChanged(this.selectedCoordSetId);
        } else if (this.templateCoordSets.length != 0) {
            this.selectedCoordSetId = this.templateCoordSets[0].id;
            this.selectedCoordSetIdChanged(this.selectedCoordSetId);
        }
    }

    private initSelectedDispGroup(): void {
        if (this.context == null) return;

        let setName = (name) => {
            for (let dispGroup of this.dispGroups) {
                if (DispGroup.groupName(dispGroup) == name) {
                    this.selectedDispGroup = dispGroup;
                    break;
                }
            }
        };

        let name = this.context.targetDispGroupName;

        if (name != null) setName(name);
        else if (this.coordSet.editDefaultVertexGroupName != null)
            setName(this.coordSet.editDefaultVertexGroupName);
    }
}
