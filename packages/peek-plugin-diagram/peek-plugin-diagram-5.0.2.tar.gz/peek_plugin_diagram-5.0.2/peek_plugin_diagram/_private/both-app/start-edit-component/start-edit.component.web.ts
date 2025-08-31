import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { DiagramCoordSetService } from "@peek/peek_plugin_diagram/DiagramCoordSetService";
import { BranchDetailTuple, BranchService } from "@peek/peek_plugin_branch";
import { BehaviorSubject, Subject } from "rxjs";

import { PrivateDiagramCoordSetService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramCoordSetService";
import {
    PopupEditBranchSelectionArgs,
    PrivateDiagramBranchService,
} from "@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchService";

import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { UserService } from "@peek/peek_core_user";

@Component({
    selector: "pl-diagram-start-edit",
    templateUrl: "start-edit.component.web.html",
    styleUrls: ["start-edit.component.web.scss"],
})
export class StartEditComponent extends NgLifeCycleEvents implements OnInit {
    popupShown: boolean = false;

    @Input("coordSetKey")
    coordSetKey: string;

    @Input("modelSetKey")
    modelSetKey: string;

    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;

    protected readonly NEW_TAB = 0;
    protected readonly EXISTING_TAB = 1;

    barIndex: number = 0;
    selectedBranch: BranchDetailTuple = null;
    newBranch: BranchDetailTuple = new BranchDetailTuple();

    private _filterText: string = "";
    private _showOnlyMine: boolean = true;
    private _sortByDate: boolean = true;

    items$ = new BehaviorSubject<BranchDetailTuple[]>([]);
    private allItems: BranchDetailTuple[] = [];

    private unsubSubject = new Subject<void>();

    constructor(
        private branchService: PrivateDiagramBranchService,
        abstractCoordSetService: DiagramCoordSetService,
        private globalBranchService: BranchService,
        private balloonMsg: BalloonMsgService,
        private userService: UserService,
    ) {
        super();

        this.branchService.popupEditBranchSelectionObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((v: PopupEditBranchSelectionArgs) => this.openPopup(v));
    }

    override ngOnInit() {}

    closePopup(): void {
        this.popupShown = false;

        // Discard the integration additions
        this.unsubSubject.next();
        this.allItems = [];
        this.refilter();
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
        this._filterText = value;
        this.refilter();
    }

    private refilter(): void {
        const filtByStr = (i: BranchDetailTuple) => {
            return (
                this._filterText.length === 0 ||
                i.name.toLowerCase().indexOf(this._filterText.toLowerCase()) !==
                    -1
            );
        };

        const filtByName = (i: BranchDetailTuple) => {
            return (
                !this._showOnlyMine ||
                i.userName == this.userService.userDetails.userId
            );
        };

        function compDate(
            ao: BranchDetailTuple,
            bo: BranchDetailTuple,
        ): -1 | 0 | 1 {
            const diff = bo.createdDate.getTime() - ao.createdDate.getTime();
            return diff == 0 ? 0 : diff < 0 ? -1 : 1;
        }

        function compStr(
            ao: BranchDetailTuple,
            bo: BranchDetailTuple,
        ): -1 | 0 | 1 {
            const a = ao.name.toLowerCase();
            const b = bo.name.toLowerCase();
            return a == b ? 0 : a < b ? -1 : 1;
        }

        let items = this.allItems.filter((i) => filtByStr(i) && filtByName(i));

        if (this._sortByDate) {
            items = items.sort(compDate);
        } else {
            items = items.sort(compStr);
        }
        this.items$.next(items);
    }

    // --------------------
    //

    noAllItems(): boolean {
        return this.allItems.length === 0;
    }

    noItems(): boolean {
        return (
            this.items.length == 0 &&
            (this._filterText.length === 0 || this.noAllItems())
        );
    }

    noFilteredItems(): boolean {
        return this.items.length == 0 && this._filterText.length !== 0;
    }

    isBranchSelected(item: BranchDetailTuple): boolean {
        return (
            item != null &&
            this.selectedBranch != null &&
            item.id == this.selectedBranch.id
        );
    }

    selectBranch(item: BranchDetailTuple): void {
        this.selectedBranch = item;
    }

    startEditing() {
        let branchToEdit = null;

        if (this.barIndex == this.NEW_TAB) {
            let nb = this.newBranch;
            if (nb.name == null || nb.name.length == 0) {
                this.balloonMsg.showWarning(
                    "Name must be supplied to create a branch",
                );
                return;
            }

            nb.key = `${nb.userName}|${nb.createdDate.getTime()}|${nb.name}`;

            this.globalBranchService
                .createBranch(nb)
                .catch((e) =>
                    this.balloonMsg.showError(`Failed to create branch : ${e}`),
                );

            branchToEdit = this.newBranch;
        } else if (this.barIndex == this.EXISTING_TAB) {
            if (this.selectedBranch == null) {
                this.balloonMsg.showWarning("You must select a branch to edit");
                return;
            }

            branchToEdit = this.selectedBranch;
        }

        this.branchService.startEditing(
            this.modelSetKey,
            this.coordSetKey,
            branchToEdit.key,
        );
        this.closePopup();
    }

    protected openPopup({
        coordSetKey,
        modelSetKey,
    }: {
        coordSetKey: string;
        modelSetKey: string;
    }) {
        this.unsubSubject.next();
        const userDetail = this.userService.userDetails;

        this.barIndex = 0;
        this.selectedBranch = null;

        this.newBranch = new BranchDetailTuple();
        this.newBranch.modelSetKey = this.modelSetKey;
        this.newBranch.createdDate = new Date();
        this.newBranch.updatedDate = new Date();
        this.newBranch.userName = userDetail.userName;

        // let coordSet = this.coordSetService.coordSetForKey(coordSetKey);
        console.log("Opening Start Edit popup");

        this.globalBranchService
            .branches$(this.modelSetKey)
            .pipe(takeUntil(this.unsubSubject))
            .subscribe((tuples: BranchDetailTuple[]) => {
                this.allItems = tuples;
                this.refilter();
            });

        this.popupShown = true;
    }
}
