import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { HeaderService } from "@synerty/peek-plugin-base-js";

import {
    PopupLayerSelectionArgsI,
    PrivateDiagramConfigService,
} from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramConfigService";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { DispLayer } from "@peek/peek_plugin_diagram/_private/lookups";

import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "pl-diagram-view-select-layers",
    templateUrl: "select-layers.component.web.html",
    styleUrls: ["select-layers.component.web.scss"],
})
export class SelectLayersComponent extends NgLifeCycleEvents implements OnInit {
    popupShown: boolean = false;

    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("model")
    model: PeekCanvasModel;

    @Input("config")
    config: PeekCanvasConfig;

    allItems: DispLayer[] = [];
    collapsedLayers: Set<number> = new Set();

    items$ = new BehaviorSubject<DispLayer[]>([]);

    private coordSetService: PrivateDiagramCoordSetService;

    private _filterText: string = "";

    constructor(
        private headerService: HeaderService,
        private lookupService: PrivateDiagramLookupService,
        private configService: PrivateDiagramConfigService,
        abstractCoordSetService: DiagramCoordSetService,
    ) {
        super();

        this.coordSetService = <PrivateDiagramCoordSetService>(
            abstractCoordSetService
        );

        this.configService
            .popupLayerSelectionObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((v: PopupLayerSelectionArgsI) => this.openPopup(v));
    }

    override ngOnInit() {}

    closePopup(): void {
        this.popupShown = false;
        this.allItems = [];
        this.collapsedLayers.clear();
        this.refilter();
    }

    noItems(): boolean {
        return this.items.length == 0;
    }

    get items(): DispLayer[] {
        return this.items$.value;
    }

    get filterText(): string {
        return this._filterText;
    }

    set filterText(value: string) {
        this._filterText = value.toLowerCase();
        this.refilter();
    }

    get isFilterActive(): boolean {
        return this._filterText.length > 0;
    }

    isLayerCollapsed(layer: DispLayer): boolean {
        return this.collapsedLayers.has(layer.id);
    }

    toggleLayerCollapse(layer: DispLayer): void {
        if (this.collapsedLayers.has(layer.id)) {
            this.collapsedLayers.delete(layer.id);
        } else {
            this.collapsedLayers.add(layer.id);
        }
        this.refilter();
    }

    isLayerVisible(layer: DispLayer): boolean {
        if (layer.parentLayer) {
            if (this.collapsedLayers.has(layer.parentLayer.id)) {
                return false;
            }
            return this.isLayerVisible(layer.parentLayer);
        }
        return true;
    }

    shouldShowLayer(layer: DispLayer): boolean {
        const matchesFilter =
            this._filterText.length === 0 ||
            layer.name.toLowerCase().indexOf(this._filterText) !== -1;

        if (!matchesFilter) {
            return false;
        }

        if (this.isFilterActive) {
            return true;
        }

        return this.isLayerVisible(layer);
    }

    getVisibleChildren(layer: DispLayer): DispLayer[] {
        if (this.isFilterActive) {
            return [];
        }

        if (this.isLayerCollapsed(layer)) {
            return [];
        }
        return layer.childLayerSortedByName.filter((child) =>
            this.shouldShowLayer(child),
        );
    }

    private refilter(): void {
        if (this.isFilterActive) {
            const allMatchingLayers = this.allItems.filter(
                (layer) =>
                    layer.name.toLowerCase().indexOf(this._filterText) !== -1,
            );
            this.items$.next(allMatchingLayers);
        } else {
            const rootLayers = this.allItems.filter(
                (layer) => layer.parentId === null,
            );
            const filteredRoots = rootLayers.filter((layer) =>
                this.shouldShowLayer(layer),
            );
            this.items$.next(filteredRoots);
        }
    }

    toggleLayerVisible(layer: DispLayer): void {
        const currentValue = layer.visible;
        let newValue: boolean | null;

        if (currentValue === null) {
            newValue = true;
        } else if (currentValue === true) {
            newValue = false;
        } else {
            newValue = null;
        }

        layer.visible = newValue;
        if (this.model != null) this.model.recompileModel();
    }

    toggleAllDescendants(parentLayer: DispLayer, visible: boolean): void {
        const descendants = this.getDescendants(parentLayer);

        parentLayer.visible = visible;

        for (const descendant of descendants) {
            descendant.visible = visible;
        }

        if (this.model != null) this.model.recompileModel();
    }

    resetToDefaults(layer: DispLayer): void {
        layer.resetToDefaultVisible();
        if (this.model != null) this.model.recompileModel();
    }

    resetAllToDefaults(parentLayer: DispLayer): void {
        const descendants = this.getDescendants(parentLayer);

        parentLayer.resetToDefaultVisible();

        for (const descendant of descendants) {
            descendant.resetToDefaultVisible();
        }

        if (this.model != null) this.model.recompileModel();
    }

    private getDescendants(parentLayer: DispLayer): DispLayer[] {
        const descendants: DispLayer[] = [...parentLayer.childLayers];
        for (const childLayer of parentLayer.childLayers) {
            descendants.push(...this.getDescendants(childLayer));
        }
        return descendants;
    }

    protected openPopup({
        coordSetKey: coordSetKey,
        modelSetKey: modelSetKey,
    }: {
        coordSetKey: string;
        modelSetKey: string;
    }) {
        let coordSet = this.coordSetService.coordSetForKey(
            modelSetKey,
            coordSetKey,
        );
        console.log("Opening Layer Select popup");

        this.allItems = this.lookupService.layersOrderedByOrder(
            coordSet.modelSetId,
        );
        this.collapsedLayers.clear();
        this.refilter();

        this.popupShown = true;
    }
}