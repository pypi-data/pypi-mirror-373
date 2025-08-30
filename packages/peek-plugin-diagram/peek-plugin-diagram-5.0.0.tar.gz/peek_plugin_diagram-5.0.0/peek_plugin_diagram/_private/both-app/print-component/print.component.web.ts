import { Component, EventEmitter, OnInit, Output } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { DiagramSnapshotService } from "@peek/peek_plugin_diagram/DiagramSnapshotService";
import { HeaderService } from "@synerty/peek-plugin-base-js";

import * as $ from "jquery";

@Component({
    selector: "pl-diagram-print",
    templateUrl: "print.component.web.html",
    styleUrls: ["print.component.web.scss"],
})
export class PrintComponent extends NgLifeCycleEvents implements OnInit {
    @Output("closePopup")
    closePopupEmitter = new EventEmitter();
    src: string | null;
    private footerClass = "peek-footer";

    constructor(
        private headerService: HeaderService,
        private snapshotService: DiagramSnapshotService,
    ) {
        super();
    }

    override ngOnInit() {
        console.log("Opening Start Edit popup");
        this.snapshotService
            .snapshotDiagram()
            .then((src) => (this.src = src))
            .catch((e) => `Failed to load branches ${e}`);

        this.headerService.setEnabled(false);
        $(this.footerClass).hide();
    }

    // --------------------
    //

    closePopup(): void {
        this.src = null;
        this.closePopupEmitter.emit();

        this.headerService.setEnabled(true);
        $(this.footerClass).show();
    }
}
