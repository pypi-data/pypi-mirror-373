import { filter, takeUntil } from "rxjs/operators";
import { Component, Input } from "@angular/core";
import { DiagramPositionService } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { DiagramToolbarService } from "@peek/peek_plugin_diagram/DiagramToolbarService";
import { PrivateDiagramToolbarService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramToolbarService";
import { PrivateDiagramPositionService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "peek-plugin-diagram-base",
    template: ``,
})
export class DiagramComponentBase extends NgLifeCycleEvents {
    @Input("modelSetKey")
    modelSetKey: string;

    coordSetKey: string | null = null;
    nsToolbarRowSpan = 1;
    nsPopupRowSpan = 1;

    protected privatePositionService: PrivateDiagramPositionService;
    protected privateToolbarService: PrivateDiagramToolbarService;

    constructor(
        protected headerService: HeaderService,
        positionService: DiagramPositionService,
        toolbarService: DiagramToolbarService,
    ) {
        super();

        this.privatePositionService = <PrivateDiagramPositionService>(
            positionService
        );
        this.privateToolbarService = <PrivateDiagramToolbarService>(
            toolbarService
        );

        // Set the title
        this.headerService.setTitle("Loading Canvas ...");

        // Listen to the title service
        this.privatePositionService
            .titleUpdatedObservable()
            .pipe(
                takeUntil(this.onDestroyEvent),
                filter((value) => value != null),
            )
            .subscribe((title: string) => this.headerService.setTitle(title));
    }
}
