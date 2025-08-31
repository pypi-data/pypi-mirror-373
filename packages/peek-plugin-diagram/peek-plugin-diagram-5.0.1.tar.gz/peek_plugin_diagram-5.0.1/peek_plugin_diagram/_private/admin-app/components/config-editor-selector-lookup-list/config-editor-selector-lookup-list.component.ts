import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject, combineLatest, Subject } from "rxjs";
import { DiagramTupleService } from "../../services/diagram-tuple-service";
import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import {
    ConfigObjectTypeE,
    DiagramConfigStateService,
    LookupListTupleType,
    LookupTypeT,
} from "../../services/diagram-config-state-service";
import { ConfigColorLookupListTuple } from "../../tuples/config-color-lookup-list-tuple";
import { ConfigLayerLookupListTuple } from "../../tuples/config-layer-lookup-list-tuple";
import { ConfigLevelLookupListTuple } from "../../tuples/config-level-lookup-list-tuple";
import { ConfigTextStyleLookupListTuple } from "../../tuples/config-text-style-lookup-list-tuple";
import { ConfigLineStyleLookupListTuple } from "../../tuples/config-line-style-lookup-list-tuple";

@Component({
    selector: "pl-diagram-config-editor-selector-lookup-list",
    templateUrl: "config-editor-selector-lookup-list.component.html",
    styleUrls: ["config-editor-selector-lookup-list.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigEditorSelectorLookupListComponent extends NgLifeCycleEvents {
    private unsub$ = new Subject<void>();
    protected showList$ = new BehaviorSubject<boolean>(false);
    protected listItems$ = new BehaviorSubject<LookupListTupleType[]>([]);
    protected filterText$ = new BehaviorSubject<string>("");
    protected filteredItems$ = new BehaviorSubject<LookupListTupleType[]>([]);
    protected selectedItemId: number | null = null;

    private selectedObjectType: ConfigObjectTypeE | null = null;

    constructor(
        private tupleService: DiagramTupleService,
        private configStateService: DiagramConfigStateService,
    ) {
        super();

        this.configStateService.lookupListConfigSelected$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((value) => {
                this.processLookupSelected(value);
            });

        // Setup filtering logic
        combineLatest([this.listItems$, this.filterText$])
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(([items, filterText]) => {
                if (!filterText) {
                    this.filteredItems$.next(items);
                    return;
                }

                const filtered = items.filter(
                    (item) =>
                        item.name
                            .toLowerCase()
                            .includes(filterText.toLowerCase()) ||
                        (item.importHash &&
                            item.importHash
                                .toLowerCase()
                                .includes(filterText.toLowerCase())),
                );
                this.filteredItems$.next(filtered);
            });
    }

    private processLookupSelected(value: [LookupTypeT, number]) {
        this.unsub$.next();
        if (value == null) {
            this.showList$.next(false);
            return;
        }

        const [objectType, objectId] = value;
        this.selectedObjectType = objectType;

        let ts: TupleSelector | null = null;
        switch (objectType) {
            case ConfigObjectTypeE.ColorLookup:
                ts = new TupleSelector(ConfigColorLookupListTuple.tupleName, {
                    modelSetId: objectId,
                });
                break;

            case ConfigObjectTypeE.LayerLookup:
                ts = new TupleSelector(ConfigLayerLookupListTuple.tupleName, {
                    modelSetId: objectId,
                });
                break;

            case ConfigObjectTypeE.LevelLookup:
                ts = new TupleSelector(ConfigLevelLookupListTuple.tupleName, {
                    canvasId: objectId,
                });
                break;

            case ConfigObjectTypeE.LineStyleLookup:
                ts = new TupleSelector(
                    ConfigLineStyleLookupListTuple.tupleName,
                    {
                        modelSetId: objectId,
                    },
                );
                break;

            case ConfigObjectTypeE.TextStyleLookup:
                ts = new TupleSelector(
                    ConfigTextStyleLookupListTuple.tupleName,
                    {
                        modelSetId: objectId,
                    },
                );
                break;
        }

        this.tupleService.observer
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(takeUntil(this.unsub$))
            .subscribe(async (tuples: Tuple[]) => {
                this.showList$.next(true);
                this.listItems$.next(tuples as any);
            });
    }

    onListItemClick(item: LookupListTupleType) {
        this.selectedItemId = item.id;
        this.configStateService.selectConfigObject(
            this.selectedObjectType,
            item.id,
        );
    }

    isItemSelected(itemId: number): boolean {
        return this.selectedItemId === itemId;
    }

    onFilterChange(event: Event) {
        const filterValue = (event.target as HTMLInputElement).value;
        this.filterText$.next(filterValue);
    }
}
