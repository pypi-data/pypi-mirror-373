import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnInit,
} from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleDataLoaderDelegate,
    TupleSelector,
} from "@synerty/vortexjs";
import { DispLevel } from "@peek/peek_plugin_diagram/_private/lookups";
import {
    AdminContentWrapperTupleDataLoaderComponent,
    AdminPanelHeaderForTupleLoaderDelegateComponent,
    BalloonMsgService,
} from "@synerty/peek-plugin-base-js";
import { filter, first, map, takeUntil } from "rxjs/operators";
import { DiagramTupleService } from "../../services/diagram-tuple-service";
import {
    ConfigObjectTypeE,
    DiagramConfigStateService,
    NewLookupWithCoordSetI,
} from "../../services/diagram-config-state-service";
import { ConfigLevelLookupDataLoaderTuple } from "../../tuples/config-level-lookup-data-loader-tuple";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { CommonModule } from "@angular/common";
import { NzInputModule } from "ng-zorro-antd/input";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzButtonModule } from "ng-zorro-antd/button";

@Component({
    selector: "pl-diagram-config-edit-lookup-level",
    templateUrl: "./config-edit-lookup-level.component.html",
    styleUrls: ["./config-edit-lookup-level.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
    standalone: true,
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        NzCardModule,
        NzFormModule,
        NzDividerModule,
        NzSwitchModule,
        NzInputModule,
        NzInputNumberModule,
        NzButtonModule,
        AdminPanelHeaderForTupleLoaderDelegateComponent,
        AdminContentWrapperTupleDataLoaderComponent,
    ],
})
export class ConfigEditLookupLevelComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    delegate: TupleDataLoaderDelegate<ConfigLevelLookupDataLoaderTuple>;

    @Input()
    diagramConfigStateService: DiagramConfigStateService;

    @Input()
    createMode: NewLookupWithCoordSetI | null = null;

    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleService: DiagramTupleService,
    ) {
        super();
    }

    override ngOnInit() {
        this.delegate = new TupleDataLoaderDelegate(
            this,
            this.tupleService.userUuid$,
        );
        this.tupleService.dataLoader.addDelegate<ConfigLevelLookupDataLoaderTuple>(
            ConfigLevelLookupDataLoaderTuple.tupleName,
            this.delegate,
            this,
        );

        if (this.createMode) {
            this.delegate.selector$.next(null);
            const data = new ConfigLevelLookupDataLoaderTuple();
            data.item = new DispLevel();
            data.item.coordSetId = this.createMode.coordSetId;
            data.item.name = this.createMode.name;
            data.item.importHash = this.createMode.importHash;
            this.delegate.data = data;
            this.delegate.validateForm();

            this.delegate.data$
                .pipe(takeUntil(this.onDestroyEvent))
                .pipe(filter((data) => data.item.id != null))
                .pipe(first())
                .subscribe((data: any) => {
                    this.createMode.result = {
                        importHash: data.item.importHash,
                        id: data.item.id,
                    };
                    this.createMode = null;
                });
        }

        this.diagramConfigStateService.lookupItemConfigSelected$
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(
                map((value) => {
                    if (value === null) return null;
                    const [objectType, objectId] = value;

                    return objectType === ConfigObjectTypeE.LevelLookup
                        ? objectId
                        : null;
                }),
            )
            .subscribe((objectId) => {
                if (objectId == null) {
                    this.delegate.selector$.next(null);
                    return;
                }

                this.delegate.selector$.next(
                    new TupleSelector(
                        ConfigLevelLookupDataLoaderTuple.tupleName,
                        {
                            id: objectId,
                        },
                    ),
                );
            });
    }
}
