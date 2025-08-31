import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    DiagramConfigStateService,
    ConfigObjectTypeE,
} from "../../services/diagram-config-state-service";
import { BehaviorSubject } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { takeUntil, map } from "rxjs/operators";

@Component({
    selector: "pl-diagram-config-editor-tab",
    templateUrl: "config-editor-tab.component.html",
    styleUrls: ["config-editor-tab.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigEditorTabComponent extends NgLifeCycleEvents {
    // BehaviorSubjects to control component visibility
    showModelSet$ = new BehaviorSubject<boolean>(false);
    showCanvas$ = new BehaviorSubject<boolean>(false);
    showColor$ = new BehaviorSubject<boolean>(false);
    showLayer$ = new BehaviorSubject<boolean>(false);
    showLevel$ = new BehaviorSubject<boolean>(false);
    showTextStyle$ = new BehaviorSubject<boolean>(false);
    showLineStyle$ = new BehaviorSubject<boolean>(false);

    constructor(
        protected diagramConfigStateService: DiagramConfigStateService,
    ) {
        super();

        // Subscribe to model set changes
        this.diagramConfigStateService.modelConfigSelected$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((modelSetId: number | null) => {
                this.showModelSet$.next(modelSetId != null);
            });

        // Subscribe to canvas changes
        this.diagramConfigStateService.canvasConfigSelected$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((canvasId: number | null) => {
                this.showCanvas$.next(canvasId != null);
            });

        // Subscribe to lookup item changes
        this.diagramConfigStateService.lookupListConfigSelected$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((value) => {
                if (value === null) {
                    this.showColor$.next(false);
                    this.showLayer$.next(false);
                    this.showLevel$.next(false);
                    this.showTextStyle$.next(false);
                    this.showLineStyle$.next(false);
                    return;
                }

                const [objectType, objectId] = value;
                this.showColor$.next(
                    objectType === ConfigObjectTypeE.ColorLookup,
                );
                this.showLayer$.next(
                    objectType === ConfigObjectTypeE.LayerLookup,
                );
                this.showLevel$.next(
                    objectType === ConfigObjectTypeE.LevelLookup,
                );
                this.showTextStyle$.next(
                    objectType === ConfigObjectTypeE.TextStyleLookup,
                );
                this.showLineStyle$.next(
                    objectType === ConfigObjectTypeE.LineStyleLookup,
                );
            });
    }
}
