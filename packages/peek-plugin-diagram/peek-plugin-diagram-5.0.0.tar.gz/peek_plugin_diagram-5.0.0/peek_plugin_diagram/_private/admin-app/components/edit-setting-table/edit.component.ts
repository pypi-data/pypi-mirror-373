import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import {
    diagramFilt,
    SettingPropertyTuple,
} from "@peek/peek_plugin_diagram/_private";

@Component({
    selector: "pl-diagram-edit-setting",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
})
export class EditSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingPropertyTuple[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(true);

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.SettingProperty",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, diagramFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingPropertyTuple[]>tuples;
                this.items$.next(typedTuples);
                this.loading$.next(false);
            });
    }

    protected readonly loader: TupleLoader;

    protected async saveClicked(): Promise<void> {
        try {
            await this.loader.save();
            this.balloonMsg.showSuccess("Save Successful");
        } catch (e) {
            this.balloonMsg.showError(`${e}`);
        }
    }

    protected async resetClicked(): Promise<void> {
        try {
            await this.loader.load();
            this.balloonMsg.showSuccess("Reset Successful");
        } catch (e) {
            this.balloonMsg.showError(`${e}`);
        }
    }
}
