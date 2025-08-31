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
import { DispLineStyle } from "@peek/peek_plugin_diagram/_private/lookups";
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
    NewLookupWithModelSetI,
} from "../../services/diagram-config-state-service";
import { ConfigLineStyleLookupDataLoaderTuple } from "../../tuples/config-line-style-lookup-data-loader-tuple";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { CommonModule } from "@angular/common";
import { NzInputModule } from "ng-zorro-antd/input";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzSelectModule } from "ng-zorro-antd/select";

@Component({
    selector: "pl-diagram-config-edit-lookup-line-style",
    templateUrl: "./config-edit-lookup-line-style.component.html",
    styleUrls: ["./config-edit-lookup-line-style.component.scss"],
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
        NzSelectModule,
        AdminPanelHeaderForTupleLoaderDelegateComponent,
        AdminContentWrapperTupleDataLoaderComponent,
    ],
})
export class ConfigEditLookupLineStyleComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    delegate: TupleDataLoaderDelegate<ConfigLineStyleLookupDataLoaderTuple>;
    capStyleOptions = [
        { label: "Butt", value: "butt" },
        { label: "Round", value: "round" },
        { label: "Square", value: "square" },
    ];

    joinStyleOptions = [
        { label: "Bevel", value: "bevel" },
        { label: "Round", value: "round" },
        { label: "Miter", value: "miter" },
    ];

    @Input()
    diagramConfigStateService: DiagramConfigStateService;

    @Input()
    createMode: NewLookupWithModelSetI | null = null;

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
        this.tupleService.dataLoader.addDelegate<ConfigLineStyleLookupDataLoaderTuple>(
            ConfigLineStyleLookupDataLoaderTuple.tupleName,
            this.delegate,
            this,
        );

        if (this.createMode) {
            this.delegate.selector$.next(null);
            const data = new ConfigLineStyleLookupDataLoaderTuple();
            data.item = new DispLineStyle();
            data.item.modelSetId = this.createMode.modelSetId;
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

                    return objectType === ConfigObjectTypeE.LineStyleLookup
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
                        ConfigLineStyleLookupDataLoaderTuple.tupleName,
                        {
                            id: objectId,
                        },
                    ),
                );
            });
    }
}
