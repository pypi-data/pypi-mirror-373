import { ChangeDetectionStrategy, Component } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import { DiagramConfigStateService } from "../../services/diagram-config-state-service";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "pl-diagram-config-edit-model-set",
    templateUrl: "./config-edit-model-set.component.html",
    styleUrls: ["./config-edit-model-set.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigEditModelSetComponent extends NgLifeCycleEvents {
    protected show$ = new BehaviorSubject<boolean>(false);

    constructor(
        protected diagramConfigStateService: DiagramConfigStateService,
    ) {
        super();

        this.diagramConfigStateService.modelConfigSelected$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((canvasId: number | null) => {
                this.show$.next(canvasId != null);
            });
    }
}
