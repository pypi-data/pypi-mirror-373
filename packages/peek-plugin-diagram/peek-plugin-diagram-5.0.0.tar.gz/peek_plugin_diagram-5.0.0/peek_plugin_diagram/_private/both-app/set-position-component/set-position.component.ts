import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DiagramPositionByCoordSetI,
    DiagramPositionByKeyI,
    DiagramPositionI,
    PrivateDiagramPositionService,
} from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";
import { filter, first, map, takeUntil } from "rxjs/operators";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { OptionalPositionArgsI } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { DispKeyLocationTuple } from "@peek/peek_plugin_diagram/_private/location-loader/DispKeyLocationTuple";
import { PrivateDiagramLocationLoaderService } from "@peek/peek_plugin_diagram/_private/location-loader";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { GridObservable } from "../cache/GridObservable.web";
import { combineLatest, Subject } from "rxjs";

interface PositionToSelectI {
    position: DispKeyLocationTuple;
    coordSet: ModelCoordSet;
    opts: OptionalPositionArgsI;
}

@Component({
    selector: "pl-diagram-set-position",
    templateUrl: "set-position.component.html",
    styleUrls: ["set-position.component.scss"],
})
export class SetPositionComponent extends NgLifeCycleEvents implements OnInit {
    /** Set Position Component
     *
     * This should probably be changed to controller or service.
     *
     */
    @Input("modelSetKey")
    modelSetKey: string;

    @Input("isReadyCallable")
    isReadyCallable: any;

    @Input("config")
    config: PeekCanvasConfig;

    @Input("model")
    model: PeekCanvasModel;

    private _isVisible: boolean = false;

    positions: PositionToSelectI[] = [];
    private coordSetChangeUnsub$ = new Subject<void>();

    constructor(
        private balloonMsg: BalloonMsgService,
        private privatePosService: PrivateDiagramPositionService,
        private coordSetService: PrivateDiagramCoordSetService,
        private branchService: PrivateDiagramBranchService,
        private locationIndexService: PrivateDiagramLocationLoaderService,
        private gridObservable: GridObservable,
    ) {
        super();
    }

    override ngOnInit() {
        combineLatest({
            coordReady: this.coordSetService.isReadyObservable(),
            gridReady: this.gridObservable.isReadyObservable(),
        })
            .pipe(
                takeUntil(this.onDestroyEvent),
                map((data) => data.coordReady && data.gridReady),
                filter((ready) => ready),
                first(),
            )
            .subscribe(() => {
                this.setupSubscriptions();
            });
    }

    private setupSubscriptions() {
        console.log("SetPositionComponent.setupSubscriptions");
        // Watch the positionByCoordSet observable
        this.privatePosService
            .positionByCoordSetObservable()
            .pipe(
                takeUntil(this.onDestroyEvent),
                filter((value) => value != null),
            )
            .subscribe((data: DiagramPositionByCoordSetI) => {
                this.privatePosService.clearPositionByCoordSetObservable();
                this.positionByCoordSet(data);
            });

        // Watch the position observables
        this.privatePosService
            .positionByKeyObservable()
            .pipe(
                takeUntil(this.onDestroyEvent),
                filter((value) => value != null),
            )
            .subscribe((pos: DiagramPositionByKeyI) => {
                this.privatePosService.clearPositionByKeyObservable();
                this.positionByKey(
                    pos.modelSetKey,
                    pos.coordSetKey,
                    pos.opts,
                    pos.dispKeyIndexes,
                ) //
                    .catch((e) => this.balloonMsg.showError(e));
            });

        // Watch the position observables
        this.privatePosService
            .positionObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((value) => value != null))
            .subscribe((pos: DiagramPositionI) => {
                this.privatePosService.clearPositionObservable();
                this.positionByXY(pos);
            });

        // Watch the select observables
        this.privatePosService
            .selectKeysObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((value) => value != null))
            .subscribe((keys: string[]) => {
                this.privatePosService.clearSelectKeysObservable();
                this.model.selection.tryToSelectKeys(keys);
            });
    }

    private positionByCoordSet(data: DiagramPositionByCoordSetI) {
        this._isVisible = false;

        if (this.modelSetKey !== data.modelSetKey) {
            throw new Error(
                "ERROR, positionByCoordSet was called for " +
                    `modelSet ${data.modelSetKey} but we're showing` +
                    `modelSet ` +
                    this.modelSetKey,
            );
        }

        if (!this.isReadyCallable()) {
            throw new Error("Position was called before canvas is ready");
        }

        this.switchToCoordSet(data.coordSetKey);

        // Inform the position service that it's ready to go.
        console.log("SetPositionComponent.positionByCoordSet calling setReady");
        this.privatePosService.setReady();
    }

    private positionByXY(pos: DiagramPositionI) {
        // Switch only if we need to
        if (
            this.config.controller.coordSet == null ||
            this.config.controller.coordSet.key != pos.coordSetKey
        ) {
            this.switchToCoordSet(pos.coordSetKey);
        }

        this.config.updateViewPortPan({ x: pos.x, y: pos.y }); // pos confirms to PanI
        this.config.updateViewPortZoom(pos.zoom);

        if (pos.opts.highlightKey != null)
            this.model.selection.tryToSelectKeys([pos.opts.highlightKey]);

        if (pos.opts.editingBranch != null) {
            this.branchService.startEditing(
                this.modelSetKey,
                this.config.coordSet.key,
                pos.opts.editingBranch,
            );
        }

        // Inform the position service that it's ready to go.
        console.log("SetPositionComponent.positionByXY calling setReady");
        this.privatePosService.setReady();
    }

    private switchToCoordSet(coordSetKey: string) {
        this._isVisible = false;

        if (!this.isReadyCallable()) {
            throw new Error(
                "SetPositionComponent.switchToCoordSet," +
                    " returning as canvas is not ready",
            );
        }

        this.coordSetChangeUnsub$.next();
        this.coordSetService
            .diagramPrivateCoordSetTuples(this.modelSetKey)
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(takeUntil(this.coordSetChangeUnsub$))
            .subscribe((modelCoordSets: ModelCoordSet[]) => {
                const coordSet = modelCoordSets.find(
                    (cs: ModelCoordSet) => cs.key == coordSetKey,
                );
                if (coordSet == null) {
                    console.error(
                        "SetPositionComponent.switchToCoordSet," +
                            ` coordSet ${coordSetKey} not found,` +
                            ` in modelSetKey ${this.modelSetKey},`,
                    );
                    console.log(modelCoordSets);
                    return;
                }
                console.log(
                    "SetPositionComponent.switchToCoordSet," +
                        ` found coordSet ${coordSetKey},` +
                        ` in modelSetKey ${this.modelSetKey},`,
                );

                this.config.updateCoordSet(coordSet);
                this.config.invalidate();

                this.privatePosService.setTitle(`Viewing ${coordSet.name}`);
            });
    }

    async positionByKey(
        modelSetKey: string,
        coordSetKey: string | null,
        opts: OptionalPositionArgsI = {},
        dispKeyIndexes: DispKeyLocationTuple[] | null = null,
    ): Promise<void> {
        if (!this.coordSetService.isReady()) {
            throw new Error(
                "positionByKey called before coordSetService is ready",
            );
        }

        if (opts.highlightKey == null || opts.highlightKey.length == 0) {
            throw new Error("positionByKey must be passed opts.highlightKey");
        }

        if (dispKeyIndexes == null) {
            dispKeyIndexes = await this.locationIndexService.getLocations(
                modelSetKey,
                opts.highlightKey,
            );
        }

        if (dispKeyIndexes.length == 0) {
            this.balloonMsg.showError(
                `Can not locate display item ${opts.highlightKey}` +
                    ` in model set ${modelSetKey}`,
            );
        }

        this.positions = [];
        const addedPositionFingerprints = new Set<string>();

        for (const dispKeyIndex of dispKeyIndexes) {
            if (
                coordSetKey != null &&
                coordSetKey !== dispKeyIndex.coordSetKey
            ) {
                continue;
            }

            const coordSet = this.coordSetService.coordSetForKey(
                modelSetKey,
                dispKeyIndex.coordSetKey,
            );

            if (coordSet == null) {
                throw new Error(
                    "Could not find coordSet for key=" +
                        dispKeyIndex.coordSetKey,
                );
            }

            const positionFingerPrint = `
                ${dispKeyIndex.coordSetKey}
                ${Math.round(dispKeyIndex.x / 100)}
                ${Math.round(dispKeyIndex.y / 100)}
            `;

            if (addedPositionFingerprints.has(positionFingerPrint)) {
                console.log(
                    `Two very similar positions for ${opts.highlightKey} around ` +
                        `${dispKeyIndex.coordSetKey}` +
                        `${dispKeyIndex.x}` +
                        `${dispKeyIndex.y}`,
                );
                continue;
            }
            console.log(
                `Adding position fingerprint ${opts.highlightKey} around ` +
                    `${dispKeyIndex.coordSetKey}` +
                    `${dispKeyIndex.x}` +
                    `${dispKeyIndex.y}`,
            );

            addedPositionFingerprints.add(positionFingerPrint);

            this.positions.push({
                position: dispKeyIndex,
                coordSet: coordSet,
                opts: opts,
            });
        }

        if (this.positions.length === 1) {
            this.handlePositionSelected(this.positions[0]);
            return;
        }
        this._isVisible = true;
    }

    get isVisible(): boolean {
        return this._isVisible && (this.positions?.length || 0) !== 0;
    }

    set isVisible(value: boolean) {
        this._isVisible = false;
    }

    handlePositionSelected(selection: PositionToSelectI): void {
        this.positionByXY({
            coordSetKey: selection.coordSet.key,
            x: selection.position.x,
            y: selection.position.y,
            zoom: selection.coordSet.positionOnZoom,
            opts: selection.opts,
        });
        this._isVisible = false;
    }
}
