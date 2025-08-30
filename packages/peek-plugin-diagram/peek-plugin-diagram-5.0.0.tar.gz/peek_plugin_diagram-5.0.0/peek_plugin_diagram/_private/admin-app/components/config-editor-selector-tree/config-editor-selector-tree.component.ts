import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BehaviorSubject, firstValueFrom } from "rxjs";
import { NzFormatEmitEvent, NzTreeNodeOptions } from "ng-zorro-antd/core/tree";
import { DiagramTupleService } from "../../services/diagram-tuple-service";
import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import { ConfigModelSetListTuple } from "../../tuples/config-model-list-tuple";
import { takeUntil } from "rxjs/operators";
import {
    ConfigObjectTypeE,
    DiagramConfigStateService,
    isLookupType,
} from "../../services/diagram-config-state-service";
import { ConfigCanvasListTuple } from "../../tuples/config-canvas-list-tuple";

@Component({
    selector: "pl-diagram-config-editor-selector-tree",
    templateUrl: "config-editor-selector-tree.component.html",
    styleUrls: ["config-editor-selector-tree.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigEditorSelectorTreeComponent extends NgLifeCycleEvents {
    rootNodes$ = new BehaviorSubject<NzTreeNodeOptions[]>([]);

    constructor(
        private tupleService: DiagramTupleService,
        private configStateService: DiagramConfigStateService,
    ) {
        super();
        tupleService.observer
            .subscribeToTupleSelector(
                new TupleSelector(ConfigModelSetListTuple.tupleName, {}),
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(async (tuples: Tuple[]) => {
                const typedTuples = tuples as ConfigModelSetListTuple[];
                const treeNodes: NzTreeNodeOptions[] = [];
                for (const tuple of typedTuples) {
                    treeNodes.push({
                        title: tuple.name,
                        key: `${ConfigObjectTypeE.ModelSet}:${tuple.id}`,
                        isLeaf: false,
                        children: await this.loadModelSetChildren(tuple.id),
                        expanded: true,
                    });
                }
                this.rootNodes$.next(treeNodes);
            });
    }

    onNodeClick($event: NzFormatEmitEvent) {
        const node = $event.node;

        const parts = node.key.split(":");
        const objectType = parseInt(parts[0]) as ConfigObjectTypeE;
        const objectId = parseInt(parts[1]);

        const isList = parts[2] === "list";
        if (isList) {
            this.configStateService.selectConfigList(objectType, objectId);
            this.configStateService.resetConfigObject();
        } else {
            if (!isLookupType(objectType)) {
                this.configStateService.resetConfigList();
            }

            this.configStateService.selectConfigObject(objectType, objectId);
        }
    }

    async loadModelSetChildren(
        modelSetId: number,
    ): Promise<NzTreeNodeOptions[]> {
        const nodes: NzTreeNodeOptions[] = [
            {
                title: "Lookup Colors",
                key: `${ConfigObjectTypeE.ColorLookup}:${modelSetId}:list`,
                isLeaf: true,
            },
            {
                title: "Lookup Layers",
                key: `${ConfigObjectTypeE.LayerLookup}:${modelSetId}:list`,
                isLeaf: true,
            },
            {
                title: "Lookup Text Styles",
                key: `${ConfigObjectTypeE.TextStyleLookup}:${modelSetId}:list`,
                isLeaf: true,
            },
            {
                title: "Lookup Line Styles",
                key: `${ConfigObjectTypeE.LineStyleLookup}:${modelSetId}:list`,
                isLeaf: true,
            },
        ];
        const canvasConfigListItems = (await firstValueFrom(
            this.tupleService.observer.subscribeToTupleSelector(
                new TupleSelector(ConfigCanvasListTuple.tupleName, {
                    modelSetId: modelSetId,
                }),
            ),
        )) as ConfigCanvasListTuple[];

        for (const canvasListItem of canvasConfigListItems) {
            nodes.push({
                title: `Canvas ${canvasListItem.name}`,
                key: `${ConfigObjectTypeE.Canvas}:${canvasListItem.id}`,
                isLeaf: false,
                expanded: true,
                children: [
                    {
                        title: "Lookup Levels",
                        key: `${ConfigObjectTypeE.LevelLookup}:${canvasListItem.id}:list`,
                        isLeaf: true,
                    },
                ],
            });
        }

        return nodes;
    }
}
