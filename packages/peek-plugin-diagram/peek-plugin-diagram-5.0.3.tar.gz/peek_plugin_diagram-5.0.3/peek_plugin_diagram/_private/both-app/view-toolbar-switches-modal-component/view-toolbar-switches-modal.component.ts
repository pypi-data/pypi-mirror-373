import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { BehaviorSubject } from "rxjs";
import {
    DiagramToolbarBuiltinButtonEnum,
    DiagramToolbarService,
    DiagramToolButtonI,
} from "@peek/peek_plugin_diagram/DiagramToolbarService";
import { PrivateDiagramToolbarService } from "@peek/peek_plugin_diagram/_private/services";

@Component({
    selector: "pl-diagram-view-toolbar-options",
    templateUrl: "view-toolbar-switches-modal.component.html",
    styleUrls: ["view-toolbar-switches-modal.component.scss"],
})
export class ViewToolbarSwitchesModalComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    popupShown: boolean = false;

    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("config")
    config: PeekCanvasConfig;

    @Input("buttonBitmask")
    buttonBitmask: DiagramToolbarBuiltinButtonEnum;

    protected toolbarService: PrivateDiagramToolbarService;

    constructor(abstractToolbarService: DiagramToolbarService) {
        super();

        this.toolbarService = <PrivateDiagramToolbarService>(
            abstractToolbarService
        );
    }

    override ngOnInit() {}

    get options$(): BehaviorSubject<DiagramToolButtonI[]> {
        return this.toolbarService.options$;
    }

    closePopup(): void {
        this.popupShown = false;
    }

    noItems(): boolean {
        return this.items.length == 0;
    }

    private get items(): DiagramToolButtonI[] {
        return this.options$.value;
    }

    callbackOption(item: DiagramToolButtonI): void {
        item.callback();
    }

    openPopup() {
        console.log("Opening Layer Select popup");
        this.popupShown = true;
    }
}
