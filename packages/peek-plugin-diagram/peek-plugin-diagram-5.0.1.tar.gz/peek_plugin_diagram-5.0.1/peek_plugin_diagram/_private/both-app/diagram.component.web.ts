import { Component, Input } from "@angular/core";
import { DiagramPositionService } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { DiagramToolbarService } from "@peek/peek_plugin_diagram/DiagramToolbarService";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { DiagramComponentBase } from "./diagram.component";

@Component({
    selector: "peek-plugin-diagram",
    templateUrl: "diagram.component.web.html",
    styleUrls: ["diagram.component.web.scss"],
})
export class DiagramComponent extends DiagramComponentBase {
    @Input() override modelSetKey;

    constructor(
        headerService: HeaderService,
        positionService: DiagramPositionService,
        toolbarService: DiagramToolbarService,
    ) {
        super(headerService, positionService, toolbarService);
    }
}
