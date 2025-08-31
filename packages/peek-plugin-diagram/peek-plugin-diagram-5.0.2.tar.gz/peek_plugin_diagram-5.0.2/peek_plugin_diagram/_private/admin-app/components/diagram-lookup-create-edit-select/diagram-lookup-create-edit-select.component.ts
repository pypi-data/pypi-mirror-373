import { Component, Input, OnInit, Optional, Self } from "@angular/core";
import { ControlValueAccessor, NgControl } from "@angular/forms";
import { BehaviorSubject, combineLatest, Subject } from "rxjs";
import { LookupTypeE } from "@peek_admin/peek_plugin_diagram/diagram-edit-lookup-service";
import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import { PrivateDiagramTupleService } from "@peek/peek_plugin_diagram/_private/services";
import { PrivateDiagramEditLookupModalService } from "../../services/private-diagram-edit-lookup-modal-service";
import { takeUntil } from "rxjs/operators";
import { PrivateDiagramLookupListTuple } from "@peek_admin/peek_plugin_diagram/_private/private-diagram-lookup-list-tuple";

interface LookupItem {
    id: number;
    key: string;
    name: string;
}

@Component({
    selector: "pl-diagram-lookup-create-edit-select",
    templateUrl: "./diagram-lookup-create-edit-select.component.html",
    styleUrls: ["./diagram-lookup-create-edit-select.component.scss"],
})
export class DiagramLookupCreateEditSelectComponent
    extends NgLifeCycleEvents
    implements OnInit, ControlValueAccessor
{
    @Input() modelSetKey$: BehaviorSubject<string | null>;
    @Input() coordSetKey$: BehaviorSubject<string | null>;

    @Input() lookupType: LookupTypeE;

    @Input() allowClear = true;

    lookupData$ = new BehaviorSubject<LookupItem[]>([]);
    selectedValue: number | null = null;
    disabled = false;

    // ControlValueAccessor callbacks
    private onChange: (value: any) => void = () => {};
    private onTouched: () => void = () => {};

    private unsubLookupSubject = new Subject<void>();

    constructor(
        private tupleService: PrivateDiagramTupleService,
        private lookupModalService: PrivateDiagramEditLookupModalService,
        @Optional() @Self() public ngControl: NgControl,
    ) {
        super();

        // Register this as the value accessor
        if (this.ngControl) {
            this.ngControl.valueAccessor = this;
        }
    }

    override ngOnInit(): void {
        combineLatest([this.modelSetKey$, this.coordSetKey$])
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(([modelSetKey, coordSetKey]) => {
                this.unsubLookupSubject.next();
                if (
                    modelSetKey == null ||
                    (this.lookupType == LookupTypeE.LEVEL &&
                        coordSetKey == null)
                ) {
                    this.lookupData$.next([]);
                    return;
                }

                // Subscribe to line style lookups
                this.tupleService.observer
                    .subscribeToTupleSelector(
                        new TupleSelector(
                            PrivateDiagramLookupListTuple.tupleName,
                            {
                                lookupType: this.lookupType,
                                modelSetKey: modelSetKey,
                                coordSetKey:
                                    this.lookupType == LookupTypeE.LEVEL
                                        ? coordSetKey
                                        : null,
                            },
                        ),
                    )
                    .pipe(takeUntil(this.unsubLookupSubject))
                    .pipe(takeUntil(this.onDestroyEvent))
                    .subscribe((tuples: Tuple[]) => {
                        this.lookupData$.next(
                            tuples as PrivateDiagramLookupListTuple[],
                        );
                    });
            });
    }

    private get modelSetKey(): string | null {
        return this.modelSetKey$.getValue();
    }

    private get coordSetKey(): string | null {
        return this.coordSetKey$.getValue();
    }

    // ControlValueAccessor implementation
    writeValue(value: any): void {
        this.selectedValue = value;
    }

    registerOnChange(fn: any): void {
        this.onChange = fn;
    }

    registerOnTouched(fn: any): void {
        this.onTouched = fn;
    }

    setDisabledState?(isDisabled: boolean): void {
        this.disabled = isDisabled;
    }

    touch(): void {
        this.onTouched != null && this.onTouched();
    }

    onValueChange(value: number): void {
        this.selectedValue = value;
        this.onChange(value);
        this.onTouched();
    }

    async editItem(): Promise<void> {
        if (!this.selectedValue) {
            return;
        }

        await this.lookupModalService.showEditModal(
            this.modelSetKey,
            this.coordSetKey,
            this.lookupType,
            { id: this.selectedValue },
        );
    }
}
