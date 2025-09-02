import { filter, takeUntil } from "rxjs/operators";
import { Component, Input } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BranchDetailTuple, BranchService } from "@peek/peek_plugin_branch";
import { PrivateDiagramConfigService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramConfigService";
import { PrivateDiagramLookupService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramLookupService";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import { PeekCanvasConfig } from "../canvas/PeekCanvasConfig.web";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch";
import {
    DocDbPopupClosedReasonE,
    DocDbPopupService,
    DocDbPopupTypeE,
} from "@peek/peek_core_docdb";
import { BehaviorSubject } from "rxjs";
import { UserService } from "@peek/peek_core_user";

@Component({
    selector: "pl-diagram-view-select-branches",
    templateUrl: "select-branches.component.web.html",
    styleUrls: ["select-branches.component.web.scss"],
})
export class SelectBranchesComponent extends NgLifeCycleEvents {
    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("config")
    config: PeekCanvasConfig;

    popupShown: boolean = false;
    enabledBranches: { [branchKey: string]: BranchDetailTuple } = {};
    selectedGlobalBranch: BranchDetailTuple | null = null;

    private coordSetService: PrivateDiagramCoordSetService;

    private _filterText: string = "";
    private _showOnlyMine: boolean = true;
    private _sortByDate: boolean = true;

    items$ = new BehaviorSubject<BranchDetailTuple[]>([]);
    private allItems: BranchDetailTuple[] = [];

    constructor(
        private objectPopupService: DocDbPopupService,
        private configService: PrivateDiagramConfigService,
        private branchService: PrivateDiagramBranchService,
        abstractCoordSetService: DiagramCoordSetService,
        private globalBranchService: BranchService,
        private userService: UserService,
    ) {
        super();

        this.coordSetService = <PrivateDiagramCoordSetService>(
            abstractCoordSetService
        );

        this.configService
            .popupBranchesSelectionObservable()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.openPopup());

        this.objectPopupService
            .popupClosedObservable(DocDbPopupTypeE.summaryPopup)
            .pipe(
                filter(
                    (reason) =>
                        reason == DocDbPopupClosedReasonE.userClickedAction,
                ),
            )
            .subscribe(() => this.closePopupFull());

        this.objectPopupService
            .popupClosedObservable(DocDbPopupTypeE.detailPopup)
            .pipe(
                filter(
                    (reason) =>
                        reason == DocDbPopupClosedReasonE.userClickedAction,
                ),
            )
            .subscribe(() => this.closePopupFull());
    }

    closePopupFull(): void {
        this.clearBranchDetails();
        this.closePopup();
    }

    closePopup(): void {
        if (this.showBranchDetails()) {
            this.clearBranchDetails();
            return;
        }

        let branches = [];
        for (let key of Object.keys(this.enabledBranches)) {
            branches.push(this.enabledBranches[key]);
        }
        this.branchService.setVisibleBranches(branches);
        this.config.setModelNeedsCompiling();
        this.config.invalidate();

        this.popupShown = false;

        // Discard the integration additions
        this.items$.next([]);
    }

    get items(): BranchDetailTuple[] {
        return this.items$.value;
    }

    get showOnlyMine(): boolean {
        return this._showOnlyMine;
    }

    set showOnlyMine(value: boolean) {
        this._showOnlyMine = value;
        this.refilter();
    }

    get sortByDate(): boolean {
        return this._sortByDate;
    }

    set sortByDate(value: boolean) {
        this._sortByDate = value;
        this.refilter();
    }

    get filterText(): string {
        return this._filterText;
    }

    set filterText(value: string) {
        this._filterText = value.toLowerCase();
        this.refilter();
    }

    private refilter(): void {
        const filtByStr = (i: BranchDetailTuple) => {
            return (
                this._filterText.length === 0 ||
                i.name.toLowerCase().indexOf(this._filterText) !== -1
            );
        };

        const filtByName = (i: BranchDetailTuple) => {
            return (
                !this._showOnlyMine ||
                i.userName?.toLowerCase() ==
                    this.userService.userDetails.userId?.toLowerCase()
            );
        };

        const compStr = (a: string, b: string) => (a == b ? 0 : a < b ? -1 : 1);

        let items = this.allItems.filter((i) => filtByStr(i) && filtByName(i));

        if (this._sortByDate) {
            items = items.sort(
                (a, b) => b.createdDate.getTime() - a.createdDate.getTime(),
            );
        } else {
            items = items.sort((a, b) =>
                compStr(a.name.toLowerCase(), b.name.toLowerCase()),
            );
        }
        this.items$.next(items);
    }

    noItems(): boolean {
        return (
            this.items.length == 0 &&
            (this._filterText.length === 0 || this.noAllItems())
        );
    }

    noAllItems(): boolean {
        return this.allItems.length === 0;
    }

    noFilteredItems(): boolean {
        return this.items.length == 0 && this._filterText.length !== 0;
    }

    toggleBranchEnabled(branchDetail: BranchDetailTuple): void {
        if (this.enabledBranches[branchDetail.key] == null) {
            this.enabledBranches[branchDetail.key] = branchDetail;
        } else {
            delete this.enabledBranches[branchDetail.key];
        }
    }

    isBranchEnabled(branchDetail: BranchDetailTuple): boolean {
        return this.enabledBranches[branchDetail.key] != null;
    }

    branchSelected(branchDetail: BranchDetailTuple): void {
        this.selectedGlobalBranch = branchDetail;
    }

    clearBranchDetails(): void {
        this.selectedGlobalBranch = null;
    }

    showBranchDetails(): boolean {
        return this.selectedGlobalBranch != null;
    }

    protected openPopup() {
        let coordSet = this.coordSetService.coordSetForKey(
            this.modelSetKey,
            this.coordSetKey,
        );
        console.log("Opening Branch Select popup");

        // Get a list of existing diagram branches, if there are no matching diagram
        // branches, then don't show them
        let diagramKeys = this.branchService.getDiagramBranchKeys(coordSet.id);
        let diagramKeyDict: { [key: string]: boolean } = {};
        for (let key of diagramKeys) {
            diagramKeyDict[key] = true;
        }

        this.globalBranchService
            .branches(this.modelSetKey)
            .then((tuples: BranchDetailTuple[]) => {
                this.allItems = [];
                for (let item of tuples) {
                    if (diagramKeyDict[item.key] == null) continue;
                    this.allItems.push(item);
                    item.__enabled = this.enabledBranches[item.key] != null;
                }
                this.refilter();
            });
        this.allItems = [];

        this.popupShown = true;
    }
}
