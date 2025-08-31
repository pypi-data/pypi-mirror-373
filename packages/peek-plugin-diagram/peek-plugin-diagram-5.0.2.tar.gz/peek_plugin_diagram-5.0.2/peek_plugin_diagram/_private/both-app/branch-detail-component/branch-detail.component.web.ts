import { Observable } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { BranchDetailTuple, BranchService } from "@peek/peek_plugin_branch";

import { BranchTuple } from "@peek/peek_plugin_diagram/_private/branch/BranchTuple";

import {
    DocDbPopupService,
    DocDbPopupTypeE,
    DocDbPropertyTuple,
    DocDbService,
    DocumentResultI,
} from "@peek/peek_core_docdb";
import { DispFactory } from "../canvas-shapes/DispFactory";
import { PrivateDiagramPositionService } from "@peek/peek_plugin_diagram/_private/services/PrivateDiagramPositionService";
import { DiagramPositionService } from "@peek/peek_plugin_diagram/DiagramPositionService";
import { PrivateDiagramBranchContext } from "@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchContext";
import { PrivateDiagramBranchService } from "@peek/peek_plugin_diagram/_private/branch/PrivateDiagramBranchService";
import { assert } from "../DiagramUtil";
import { DispBase } from "../canvas-shapes/DispBase";
import { diagramPluginName } from "@peek/peek_plugin_diagram/_private/PluginNames";

interface AnchorDisplayItemI {
    key: string;
    header: string;
    body: string;
}

interface DispDisplayItemI {
    disp: any;
    dispDesc: string;
}

@Component({
    selector: "pl-diagram-branch-detail",
    templateUrl: "branch-detail.component.web.html",
    styleUrls: ["branch-detail.component.web.scss"],
})
export class BranchDetailComponent extends NgLifeCycleEvents implements OnInit {
    @Input("modelSetKey")
    modelSetKey: string;

    @Input("coordSetKey")
    coordSetKey: string;

    // Set in VIEW mode from select-branches
    @Input("globalBranch")
    inputGlobalBranch: BranchDetailTuple;

    // Set in EDIT mode from edit-props
    @Input("globalBranchKey")
    globalBranchKey: string;

    globalBranch: BranchDetailTuple;

    // Set in EDIT mode from edit-props
    @Input("diagramBranchTuple")
    diagramBranch: BranchTuple;

    // Set in EDIT mode from edit-props
    @Input("diagramBranchUpdatedObservable")
    diagramBranchUpdatedObservable: Observable<boolean>;

    isEditMode: boolean = false;

    anchorDocs: any[] = [];

    disps: DispDisplayItemI[] = [];

    private diagramPosService: PrivateDiagramPositionService;

    constructor(
        private objectPopupService: DocDbPopupService,
        private docDbService: DocDbService,
        diagramPosService: DiagramPositionService,
        private branchService: PrivateDiagramBranchService,
        private globalBranchService: BranchService,
    ) {
        super();

        this.diagramPosService = <PrivateDiagramPositionService>(
            diagramPosService
        );
    }

    override ngOnInit() {
        if (this.inputGlobalBranch != null) {
            this.globalBranch = this.inputGlobalBranch;
            this.globalBranchKey = this.inputGlobalBranch.key;
            this.loadDiagramBranch();
            return;
        }

        assert(this.diagramBranch != null, "diagramBranch is not set");
        assert(this.globalBranchKey != null, "globalBranchKey is not set");

        this.isEditMode = true;
        this.loadGlobalBranch();
        this.loadDiagramBranchDisps();
        this.loadDiagramBranchAnchorKeys();

        if (this.diagramBranchUpdatedObservable != null) {
            this.diagramBranchUpdatedObservable
                .pipe(takeUntil(this.onDestroyEvent))
                .subscribe(() => {
                    this.loadDiagramBranchDisps();
                    this.loadDiagramBranchAnchorKeys();
                });
        }
    }

    noAnchors(): boolean {
        return this.anchorDocs.length == 0;
    }

    noDisps(): boolean {
        return this.disps.length == 0;
    }

    positonAnchorOnDiagram(props: any[]): void {
        this.diagramPosService.positionByKey(
            this.modelSetKey,
            this.coordSetKey,
            { highlightKey: props[0].value },
        );
    }

    positonDispOnDiagram(disp: any): void {
        let Wrapper = DispFactory.wrapper(disp);
        let center = Wrapper.center(disp);

        this.diagramPosService.position(
            this.coordSetKey,
            center.x,
            center.y,
            5.0,
            Wrapper.key(disp) || {},
        );
    }

    showSummaryPopup($event: MouseEvent, result: AnchorDisplayItemI) {
        this.objectPopupService.hidePopup(DocDbPopupTypeE.tooltipPopup);
        this.objectPopupService.showPopup(
            true,
            DocDbPopupTypeE.summaryPopup,
            diagramPluginName,
            $event,
            this.modelSetKey,
            result.key,
        );
    }

    private loadGlobalBranch() {
        this.globalBranch = new BranchDetailTuple();

        this.globalBranchService
            .getBranch(this.modelSetKey, this.globalBranchKey)
            .then((globalBranch: BranchDetailTuple | null) => {
                if (globalBranch == null) {
                    console.log(
                        `ERROR: Could not load global branch for ${this.globalBranchKey}`,
                    );
                    return;
                }
                this.globalBranch = globalBranch;
            });
    }

    private loadDiagramBranch() {
        this.diagramBranch = new BranchTuple();
        this.disps = [];

        this.branchService
            .getBranch(this.modelSetKey, this.coordSetKey, this.globalBranchKey)
            .then((diagramBranch: PrivateDiagramBranchContext) => {
                this.diagramBranch = diagramBranch.branchTuple;
                this.loadDiagramBranchDisps();
                this.loadDiagramBranchAnchorKeys();
            });
    }

    private loadDiagramBranchDisps() {
        const branchDisps = this.diagramBranch.disps.filter(
            (d) => DispBase.groupId(d) == null,
        );
        this.disps = [];

        for (let disp of branchDisps) {
            const shapeStr = DispFactory.wrapper(disp).makeShapeStr(disp);

            this.disps.push({
                disp: disp,
                dispDesc: shapeStr.split("\n"),
            });
        }
    }

    private loadDiagramBranchAnchorKeys() {
        let anchorKeys = this.diagramBranch.anchorDispKeys;
        if (anchorKeys == null || anchorKeys.length == 0) {
            this.anchorDocs = [];
            return;
        }

        this.docDbService
            .getObjects(this.modelSetKey, anchorKeys)
            .then((docs: DocumentResultI) => {
                this.anchorDocs = [];

                for (let anchorDispKey of anchorKeys) {
                    let doc = docs[anchorDispKey];
                    if (doc == null) continue;

                    const props = this.docDbService.getNiceOrderedProperties(
                        doc,
                        (prop: DocDbPropertyTuple) => prop.showOnTooltip,
                    );

                    this.anchorDocs.push({
                        key: anchorDispKey,
                        header: props
                            .filter((d) => d.showInHeader)
                            .map((d) => d.value)
                            .join(", "),
                        body: props
                            .filter((d) => !d.showInHeader)
                            .map((d) => d.value)
                            .join(", "),
                    });
                }
            });
    }
}
