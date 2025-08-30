import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject, combineLatest, Subject } from "rxjs";
import { DiagramTupleService } from "../../services/diagram-tuple-service";
import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import {
    ConfigObjectTypeE,
    DiagramConfigStateService,
} from "../../services/diagram-config-state-service";
import { ConfigLayerLookupListTuple } from "../../tuples/config-layer-lookup-list-tuple";
import { NzFormatEmitEvent, NzTreeNodeOptions } from "ng-zorro-antd/core/tree";

@Component({
    selector: "pl-diagram-config-editor-selector-lookup-layer-tree",
    templateUrl: "config-editor-selector-lookup-layer-tree.component.html",
    styleUrls: ["config-editor-selector-lookup-layer-tree.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigEditorSelectorLookupLayerTreeComponent extends NgLifeCycleEvents {
    private unsub$ = new Subject<void>();
    protected showTree$ = new BehaviorSubject<boolean>(false);
    protected treeNodes$ = new BehaviorSubject<NzTreeNodeOptions[]>([]);
    protected filterText$ = new BehaviorSubject<string>("");
    protected filteredTreeNodes$ = new BehaviorSubject<NzTreeNodeOptions[]>([]);
    protected selectedItemId: number | null = null;

    private allLayers: ConfigLayerLookupListTuple[] = [];

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
        combineLatest([this.treeNodes$, this.filterText$])
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(([treeNodes, filterText]) => {
                if (!filterText) {
                    this.filteredTreeNodes$.next(treeNodes);
                    return;
                }

                const filtered = this.filterTreeNodes(treeNodes, filterText);
                this.filteredTreeNodes$.next(filtered);
            });
    }

    private processLookupSelected(value: [ConfigObjectTypeE, number]) {
        this.unsub$.next();
        if (value == null) {
            this.showTree$.next(false);
            return;
        }

        const [objectType, objectId] = value;

        // Only handle layer lookups
        if (objectType !== ConfigObjectTypeE.LayerLookup) {
            this.showTree$.next(false);
            return;
        }

        const ts = new TupleSelector(ConfigLayerLookupListTuple.tupleName, {
            modelSetId: objectId,
        });

        this.tupleService.observer
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(takeUntil(this.unsub$))
            .subscribe(async (tuples: Tuple[]) => {
                this.allLayers = tuples as ConfigLayerLookupListTuple[];
                this.showTree$.next(true);
                this.buildTreeNodes();
            });
    }

    private buildTreeNodes(): void {
        const treeNodes = this.buildLayerTree(this.allLayers);
        this.treeNodes$.next(treeNodes);
    }

    private buildLayerTree(
        layers: ConfigLayerLookupListTuple[],
    ): NzTreeNodeOptions[] {
        const layerMap = new Map<number, ConfigLayerLookupListTuple>();
        const rootLayers: ConfigLayerLookupListTuple[] = [];

        // Create a map for quick lookup and identify root layers
        layers.forEach((layer) => {
            layerMap.set(layer.id, layer);
            if (!layer.parentId) {
                rootLayers.push(layer);
            }
        });

        // Build tree recursively
        const buildNode = (
            layer: ConfigLayerLookupListTuple,
        ): NzTreeNodeOptions => {
            const children = layers
                .filter((l) => l.parentId === layer.id)
                .map((child) => buildNode(child));

            return {
                title: `${layer.name} (${layer.importHash})`,
                key: layer.id.toString(),
                isLeaf: children.length === 0,
                children: children,
                expanded: true,
            };
        };

        return rootLayers.map((layer) => buildNode(layer));
    }

    private filterTreeNodes(
        nodes: NzTreeNodeOptions[],
        filterText: string,
    ): NzTreeNodeOptions[] {
        const filterLower = filterText.toLowerCase();

        const filterNode = (
            node: NzTreeNodeOptions,
        ): NzTreeNodeOptions | null => {
            const matchesFilter = node.title
                ?.toString()
                .toLowerCase()
                .includes(filterLower);

            let filteredChildren: NzTreeNodeOptions[] = [];
            if (node.children) {
                filteredChildren = node.children
                    .map((child) => filterNode(child))
                    .filter((child) => child !== null) as NzTreeNodeOptions[];
            }

            // Include node if it matches or has matching children
            if (matchesFilter || filteredChildren.length > 0) {
                return {
                    ...node,
                    children: filteredChildren,
                    expanded: true, // Expand filtered nodes
                };
            }

            return null;
        };

        return nodes
            .map((node) => filterNode(node))
            .filter((node) => node !== null) as NzTreeNodeOptions[];
    }

    onNodeClick($event: NzFormatEmitEvent): void {
        const node = $event.node;
        const layerId = parseInt(node.key);

        this.selectedItemId = layerId;
        this.configStateService.selectConfigObject(
            ConfigObjectTypeE.LayerLookup,
            layerId,
        );
    }

    isNodeSelected(node: NzTreeNodeOptions): boolean {
        return this.selectedItemId === parseInt(node.key);
    }

    onFilterChange(event: Event): void {
        const filterValue = (event.target as HTMLInputElement).value;
        this.filterText$.next(filterValue);
    }
}
