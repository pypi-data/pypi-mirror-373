import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnInit,
} from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataLoaderDelegate,
    TupleSelector,
} from "@synerty/vortexjs";
import { DispLayer } from "@peek/peek_plugin_diagram/_private/lookups";
import {
    AdminContentWrapperTupleDataLoaderComponent,
    AdminPanelHeaderForTupleLoaderDelegateComponent,
    BalloonMsgService,
} from "@synerty/peek-plugin-base-js";
import { filter, first, map, takeUntil } from "rxjs/operators";
import { BehaviorSubject } from "rxjs";
import { DiagramTupleService } from "../../services/diagram-tuple-service";
import {
    ConfigObjectTypeE,
    DiagramConfigStateService,
    NewLookupWithModelSetI,
} from "../../services/diagram-config-state-service";
import { ConfigLayerLookupDataLoaderTuple } from "../../tuples/config-layer-lookup-data-loader-tuple";
import { ConfigLayerLookupListTuple } from "../../tuples/config-layer-lookup-list-tuple";
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
import { NzCheckboxModule } from "ng-zorro-antd/checkbox";

@Component({
    selector: "pl-diagram-config-edit-lookup-layer",
    templateUrl: "./config-edit-lookup-layer.component.html",
    styleUrls: ["./config-edit-lookup-layer.component.scss"],
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
        NzCheckboxModule,
    ],
})
export class ConfigEditLookupLayerComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    delegate: TupleDataLoaderDelegate<ConfigLayerLookupDataLoaderTuple>;
    availableParentLayers$ = new BehaviorSubject<ConfigLayerLookupListTuple[]>(
        [],
    );

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
        this.tupleService.dataLoader.addDelegate<ConfigLayerLookupDataLoaderTuple>(
            ConfigLayerLookupDataLoaderTuple.tupleName,
            this.delegate,
            this,
        );

        if (this.createMode) {
            this.delegate.selector$.next(null);
            const data = new ConfigLayerLookupDataLoaderTuple();
            data.item = new DispLayer();
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

                    return objectType === ConfigObjectTypeE.LayerLookup
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
                        ConfigLayerLookupDataLoaderTuple.tupleName,
                        {
                            id: objectId,
                        },
                    ),
                );
            });

        this.delegate.data$
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((data) => data?.item?.modelSetId != null))
            .subscribe((data) => {
                this.loadAvailableParentLayers(
                    data.item.modelSetId,
                    data.item.id,
                );
            });
    }

    private loadAvailableParentLayers(
        modelSetId: number,
        currentLayerId: number | null,
    ): void {
        const selector = new TupleSelector(
            ConfigLayerLookupListTuple.tupleName,
            {
                modelSetId: modelSetId,
            },
        );

        this.tupleService.observer
            .subscribeToTupleSelector(selector)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const layers = tuples as ConfigLayerLookupListTuple[];
                const filteredLayers = currentLayerId
                    ? layers.filter((layer) => layer.id !== currentLayerId)
                    : layers;
                this.availableParentLayers$.next(filteredLayers);
            });
    }

    onTriStateChange(controlName: string): void {
        const control =
            this.delegate.formGroup$.getValue()?.controls[controlName];
        if (!control) return;

        const currentValue = control.value;
        let newValue: boolean | null;

        if (currentValue === null) {
            newValue = true;
        } else if (currentValue === true) {
            newValue = false;
        } else {
            newValue = null;
        }

        control.setValue(newValue);
        control.markAsDirty();
    }
}
