import { takeUntil } from "rxjs/operators";
import { Component, Input, OnInit, ViewChild } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    NzContextMenuService,
    NzDropdownMenuComponent,
} from "ng-zorro-antd/dropdown";
import {
    ContextMenuPopupI,
    ContextMenuService,
} from "../services/context-menu.service";
import { PeekCanvasEditor } from "../canvas/PeekCanvasEditor.web";
import { CopyPasteService } from "../services/copy-paste.service";
import { PeekCanvasModel } from "../canvas/PeekCanvasModel.web";
import { PeekCanvasInputEditSelectDelegate } from "../canvas-input/PeekCanvasInputEditSelectDelegate.web";

@Component({
    selector: "pl-diagram-canvas-context-menu",
    templateUrl: "canvas-context-menu.component.web.html",
    styleUrls: ["canvas-context-menu.component.web.scss"],
})
export class CanvasContextMenuComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    @Input("canvasEditor")
    canvasEditor: PeekCanvasEditor;

    @Input("model")
    model: PeekCanvasModel;

    @ViewChild("menu", { static: true })
    private menu: NzDropdownMenuComponent;

    constructor(
        private menuService: NzContextMenuService,
        private diagramContextService: ContextMenuService,
        private copyPasteService: CopyPasteService,
    ) {
        super();
        diagramContextService.openObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((event: ContextMenuPopupI) =>
                this.handleContextMenuOpen(event),
            );
    }

    override ngOnInit() {}

    handleContextMenuOpen(event: ContextMenuPopupI) {
        this.menuService.create(event, this.menu);
    }

    get canUndo(): boolean {
        return this.canvasEditor.canUndo;
    }

    handleUndo(): void {
        this.canvasEditor.doUndo();
    }

    get canRedo(): boolean {
        return this.canvasEditor.canRedo;
    }

    handleRedo(): void {
        this.canvasEditor.doRedo();
    }

    get canCopy(): boolean {
        return this.copyPasteService.canCopy;
    }

    handleCopy(): void {
        this.copyPasteService.doCopy();
    }

    get canPaste(): boolean {
        return this.copyPasteService.canPaste;
    }

    handlePaste(): void {
        this.copyPasteService.doPaste();
    }

    get canDelete(): boolean {
        return this.model.selection.hasSelection;
    }

    handleDelete(): void {
        let delegate = <PeekCanvasInputEditSelectDelegate>(
            this.canvasEditor?.canvasInput.selectedDelegate()
        );

        delegate.deleteSelectedDisps();
    }
}
