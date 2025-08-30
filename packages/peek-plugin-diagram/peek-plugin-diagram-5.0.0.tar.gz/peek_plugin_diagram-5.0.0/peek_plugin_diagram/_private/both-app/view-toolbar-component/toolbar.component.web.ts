import { take, takeUntil } from "rxjs/operators";
import { Component, EventEmitter, Input, OnInit, Output } from "@angular/core";
import {
    DiagramToolbarBuiltinButtonEnum,
    DiagramToolbarService,
    DiagramToolButtonI,
} from "@peek/peek_plugin_diagram/DiagramToolbarService";
import { PrivateDiagramToolbarService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramToolbarService";
import { PrivateDiagramConfigService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramConfigService";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchService";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { ModelCoordSet } from "@peek/peek_plugin_diagram/_private/tuples";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { DiagramPositionService } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { DocDbPopupService, DocDbPopupTypeE } from "@peek/peek_core_docdb";
import { DeviceEnrolmentService } from "@peek/peek_core_device";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "pl-diagram-view-toolbar",
    templateUrl: "toolbar.component.web.html",
    styleUrls: ["toolbar.component.web.scss"],
})
export class ToolbarComponent extends NgLifeCycleEvents implements OnInit {
    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("config")
    config: PeekCanvasConfig;

    @Input("buttonBitmask")
    buttonBitmask: DiagramToolbarBuiltinButtonEnum;

    @Output("openPrintPopup")
    openPrintPopupEmitter = new EventEmitter<void>();

    dispKey: string;
    coordSet: ModelCoordSet = new ModelCoordSet();
    shownPluginButtons: DiagramToolButtonI[] = [];
    toolbarIsOpen: boolean = false;
    coordSetsForMenu: ModelCoordSet[] = [];

    tooltipTrigger: "click" | "focus" | "hover" | null = "hover";

    protected toolbarService: PrivateDiagramToolbarService;
    private parentPluginButtons: DiagramToolButtonI[][] = [];

    readonly showOptionsCog$ = new BehaviorSubject<boolean>(false);

    constructor(
        private objectPopupService: DocDbPopupService,
        private abstractToolbarService: DiagramToolbarService,
        private branchService: PrivateDiagramBranchService,
        private configService: PrivateDiagramConfigService,
        private coordSetService: PrivateDiagramCoordSetService,
        private positionService: DiagramPositionService,
        private deviceEnrolmentService: DeviceEnrolmentService,
    ) {
        super();

        this.toolbarService = <PrivateDiagramToolbarService>(
            abstractToolbarService
        );

        this.parentPluginButtons = [];

        this.toolbarService.toolButtons$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((buttons: DiagramToolButtonI[]) => {
                this.shownPluginButtons = buttons.filter(
                    (b) => b.isActive == null,
                );
                this.parentPluginButtons = [];
            });

        this.toolbarService.options$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((options: DiagramToolButtonI[]) => {
                this.showOptionsCog = options.length != 0;
            });

        // While we're using ant.design v10, disable tooltips for field / iOS
        if (this.deviceEnrolmentService.isFieldService()) {
            this.tooltipTrigger = null;
        }
    }

    override ngOnInit() {
        if (this.config.coordSet != null) this.coordSet = this.config.coordSet;

        this.config.controller.coordSetChange
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(
                (cs) => (this.coordSet = cs != null ? cs : new ModelCoordSet()),
            );

        this.coordSetService
            .diagramPrivateCoordSetTuples(this.modelSetKey)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((modelCoordSets: ModelCoordSet[]) =>
                this.applyUpdatedCoordSets(modelCoordSets),
            );
    }

    private applyUpdatedCoordSets(modelCoordSets: ModelCoordSet[]) {
        this.coordSetsForMenu = modelCoordSets.filter(
            (cs: ModelCoordSet) => cs.enabled == true,
        );

        if (!this.coordSet?.key?.length) {
            return;
        }

        const coordSet = modelCoordSets.find(
            (cs: ModelCoordSet) => cs.key === this.coordSet.key,
        );

        if (coordSet == null) {
            console.error(
                "ToolbarComponent.applyUpdatedCoordSets," +
                    ` coordSet ${this.coordSet.key} not found,` +
                    ` in modelSetKey ${this.modelSetKey},`,
            );
            console.log(modelCoordSets);
            return;
        }
        console.log(
            "ToolbarComponent.applyUpdatedCoordSets," +
                ` found coordSet ${this.coordSet.key},` +
                ` in modelSetKey ${this.modelSetKey},`,
        );
        this.coordSet = coordSet;
    }

    private get showOptionsCog(): boolean {
        return this.showOptionsCog$.getValue();
    }

    private set showOptionsCog(value: boolean) {
        this.showOptionsCog$.next(value);
    }

    buttonClicked(btn: DiagramToolButtonI): void {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        if (btn.callback != null) {
            btn.callback();
        } else if (btn.children == null && btn.children.length != 0) {
            this.parentPluginButtons.push(this.shownPluginButtons);
            this.shownPluginButtons = btn.children;
        } else {
            // ??
        }
    }

    isButtonActive(btn: DiagramToolButtonI): boolean {
        if (btn.isActive == null) return false;
        return btn.isActive();
    }

    toggleToolbar(): void {
        this.toolbarIsOpen = !this.toolbarIsOpen;
    }

    isBranchesActive(): boolean {
        return this.branchService.areBranchesActive(this.coordSet.id);
    }

    showSelectBranchesButton(): boolean {
        return (
            (this.buttonBitmask &
                DiagramToolbarBuiltinButtonEnum.BUTTON_SELECT_BRANCHES) >
                0 && this.coordSet.branchesEnabled == true
        );
    }

    showSelectBranchesTooltip(): string {
        if (this.isBranchesActive())
            return "Show Branches\n(Diagram overlays are currently disabled)";
        return "Show Branches";
    }

    showExitDiagramButton(): boolean {
        return (
            (this.buttonBitmask &
                DiagramToolbarBuiltinButtonEnum.BUTTON_CHANGE_CANVAS_MENU) >
                0 && this.coordSetsForMenu.length > 1
        );
    }

    changeCoordSetMenuItemClicked(coordSet: ModelCoordSet): void {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.positionService.positionByCoordSet(this.modelSetKey, coordSet.key);
    }

    showToggleColorModeButton(): boolean {
        return (
            (this.buttonBitmask &
                DiagramToolbarBuiltinButtonEnum.BUTTON_COLOR_MODES) >
                0 && this.coordSet.lightModeEnabled
        );
    }

    isLightMode(): boolean {
        return this.config.isLightMode;
    }

    toggleColorModeButton(): void {
        this.config.isLightMode = !this.config.isLightMode;
    }

    showPrintDiagramButton(): boolean {
        return (
            (this.buttonBitmask &
                DiagramToolbarBuiltinButtonEnum.BUTTON_PRINT_DIAGRAM) !=
            0
        );
    }

    showEditDiagramButton(): boolean {
        return (
            (this.buttonBitmask &
                DiagramToolbarBuiltinButtonEnum.BUTTON_EDIT_DIAGRAM) !=
                0 &&
            this.coordSet.editEnabled == true &&
            this.coordSet.editDefaultLayerId != null &&
            this.coordSet.editDefaultLevelId != null &&
            this.coordSet.editDefaultColorId != null &&
            this.coordSet.editDefaultLineStyleId != null &&
            this.coordSet.editDefaultTextStyleId != null
        );
    }

    editDiagramClicked(): void {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.branchService.popupEditBranchSelection(
            this.modelSetKey,
            this.coordSetKey,
        );
    }

    printDiagramClicked(): void {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.openPrintPopupEmitter.next();
    }

    selectBranchesClicked(): void {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.configService.popupBranchesSelection(
            this.modelSetKey,
            this.coordSetKey,
        );
    }

    showSelectLayers(): boolean {
        return (
            (this.buttonBitmask &
                DiagramToolbarBuiltinButtonEnum.BUTTON_SELECT_LAYERS) >
            0
        );
    }

    selectLayersClicked(): void {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.configService.popupLayerSelection(
            this.modelSetKey,
            this.coordSetKey,
        );
    }

    showGoUpParentButton(): boolean {
        return this.parentPluginButtons.length != 0;
    }

    goUpParentButtonClicked(): void {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.shownPluginButtons = this.parentPluginButtons.pop();
    }

    isToolbarEmpty(): boolean {
        return this.shownPluginButtons.length == 0;
    }
}
