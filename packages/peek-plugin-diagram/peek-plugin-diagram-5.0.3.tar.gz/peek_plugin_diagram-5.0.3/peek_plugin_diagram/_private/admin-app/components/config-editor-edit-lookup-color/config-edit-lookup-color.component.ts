import {
    ChangeDetectionStrategy,
    Component,
    Input,
    OnInit,
} from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleDataLoaderDelegate,
    TupleSelector,
} from "@synerty/vortexjs";
import {
    AdminContentWrapperTupleDataLoaderComponent,
    AdminPanelHeaderForTupleLoaderDelegateComponent,
    BalloonMsgService,
} from "@synerty/peek-plugin-base-js";
import { filter, first, map, takeUntil } from "rxjs/operators";
import { DiagramTupleService } from "../../services/diagram-tuple-service";
import {
    ConfigObjectTypeE,
    DiagramConfigStateService,
    NewLookupWithModelSetI,
} from "../../services/diagram-config-state-service";
import { ConfigColorLookupDataLoaderTuple } from "../../tuples/config-color-lookup-data-loader-tuple";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { CommonModule } from "@angular/common";
import { NzInputModule } from "ng-zorro-antd/input";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzButtonModule } from "ng-zorro-antd/button";
import { DispColor } from "@peek/peek_plugin_diagram/_private/lookups";

@Component({
    selector: "pl-diagram-config-edit-lookup-color",
    templateUrl: "./config-edit-lookup-color.component.html",
    styleUrls: ["./config-edit-lookup-color.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
    standalone: true,
    imports: [
        CommonModule,
        FormsModule,
        ReactiveFormsModule,
        NzCardModule,
        NzFormModule,
        NzDividerModule,
        NzSwitchModule,
        NzInputModule,
        NzInputNumberModule,
        NzButtonModule,
        AdminPanelHeaderForTupleLoaderDelegateComponent,
        AdminContentWrapperTupleDataLoaderComponent,
    ],
})
export class ConfigEditLookupColorComponent
    extends NgLifeCycleEvents
    implements OnInit
{
    delegate: TupleDataLoaderDelegate<ConfigColorLookupDataLoaderTuple>;
    imagePreviews: { dark: string | null; light: string | null } = {
        dark: null,
        light: null,
    };

    @Input()
    diagramConfigStateService: DiagramConfigStateService;

    @Input()
    createMode: NewLookupWithModelSetI | null = null;

    constructor(
        private balloonMsg: BalloonMsgService,
        private tupleService: DiagramTupleService,
    ) {
        super();
    }

    override ngOnInit() {
        this.delegate = new TupleDataLoaderDelegate(
            this,
            this.tupleService.userUuid$,
        );
        this.tupleService.dataLoader.addDelegate<ConfigColorLookupDataLoaderTuple>(
            ConfigColorLookupDataLoaderTuple.tupleName,
            this.delegate,
            this,
        );

        if (this.createMode) {
            this.delegate.selector$.next(null);
            const data = new ConfigColorLookupDataLoaderTuple();
            data.item = new DispColor();
            data.item.modelSetId = this.createMode.modelSetId;
            data.item.name = this.createMode.name;
            data.item.importHash = this.createMode.importHash;
            this.delegate.data = data;
            this.delegate.validateForm();

            this.delegate.data$
                .pipe(takeUntil(this.onDestroyEvent))
                .pipe(filter((data) => data.item.id != null))
                .pipe(first())
                .subscribe((data: any) => {
                    this.createMode.result = {
                        importHash: data.item.importHash,
                        id: data.item.id,
                    };
                    this.createMode = null;
                });
        }

        this.diagramConfigStateService.lookupItemConfigSelected$
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(
                map((value) => {
                    if (value === null) return null;
                    const [objectType, objectId] = value;

                    return objectType === ConfigObjectTypeE.ColorLookup
                        ? objectId
                        : null;
                }),
            )
            .subscribe((objectId) => {
                if (objectId == null) {
                    this.delegate.selector$.next(null);
                    return;
                }

                this.delegate.selector$.next(
                    new TupleSelector(
                        ConfigColorLookupDataLoaderTuple.tupleName,
                        {
                            id: objectId,
                        },
                    ),
                );
            });

        // Update image previews when form group is available
        this.delegate.formGroup$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((formGroup) => {
                if (formGroup) {
                    this.updateImagePreviews();
                }
            });
    }

    handleFileUpload(event: Event, mode: "dark" | "light"): void {
        const input = event.target as HTMLInputElement;
        const formGroup = this.delegate.formGroup$.value;
        if (!formGroup) return;

        const file = input?.files?.[0];
        if (!file) return;

        // Check file size (limit to 2MB)
        if (file.size > 2 * 1024 * 1024) {
            this.balloonMsg.showError("File size exceeds 2MB limit");
            return;
        }

        // Check file type - only allow common web image formats
        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/svg+xml",
            "image/webp",
        ];
        if (!allowedTypes.includes(file.type)) {
            this.balloonMsg.showError(
                "Only JPG, PNG, GIF, SVG, and WebP images are allowed",
            );
            return;
        }

        const reader = new FileReader();

        reader.onload = (e) => {
            const base64Image = e.target?.result as string;

            // Validate the base64 string format
            if (!this.validateBase64Image(base64Image)) {
                this.balloonMsg.showError("Invalid image format");
                return;
            }

            // Validate that the image can be loaded properly
            this.validateImageLoading(base64Image, (isValid) => {
                if (!isValid) {
                    this.balloonMsg.showError(
                        "The image could not be loaded properly",
                    );
                    return;
                }

                if (mode === "dark") {
                    formGroup.get("darkFillBase64Image")?.setValue(base64Image);
                    this.imagePreviews.dark = base64Image;
                } else {
                    formGroup
                        .get("lightFillBase64Image")
                        ?.setValue(base64Image);
                    this.imagePreviews.light = base64Image;
                }
            });
        };

        reader.onerror = () => {
            this.balloonMsg.showError("Failed to read the image file");
        };

        reader.readAsDataURL(file);
    }

    updateImagePreviews(): void {
        const formGroup = this.delegate.formGroup$.value;
        if (!formGroup) return;

        this.imagePreviews.dark =
            formGroup.get("darkFillBase64Image")?.value || null;
        this.imagePreviews.light =
            formGroup.get("lightFillBase64Image")?.value || null;
    }

    clearImage(mode: "dark" | "light"): void {
        const formGroup = this.delegate.formGroup$.value;
        if (!formGroup) return;

        if (mode === "dark") {
            formGroup.get("darkFillBase64Image")?.setValue("");
            this.imagePreviews.dark = null;
        } else {
            formGroup.get("lightFillBase64Image")?.setValue("");
            this.imagePreviews.light = null;
        }
    }

    /**
     * Validates that the string is a properly formatted base64 image
     */
    private validateBase64Image(base64String: string): boolean {
        // Check if it's a data URL with base64 encoding
        if (!base64String || !base64String.startsWith("data:image/")) {
            return false;
        }

        // Verify it contains the base64 marker
        if (!base64String.includes(";base64,")) {
            return false;
        }

        // Basic structure validation passed
        return true;
    }

    /**
     * Validates that the image can be properly loaded by the browser
     */
    private validateImageLoading(
        base64String: string,
        callback: (isValid: boolean) => void,
    ): void {
        const img = new Image();
        const maxDimension = 4096; // Maximum dimension for width or height

        img.onload = () => {
            // Check if image dimensions are reasonable
            if (img.width <= 0 || img.height <= 0) {
                callback(false);
                return;
            }

            // Check maximum dimensions
            if (img.width > maxDimension || img.height > maxDimension) {
                this.balloonMsg.showError(
                    `Image dimensions exceed maximum allowed (${maxDimension}px)`,
                );
                callback(false);
                return;
            }

            callback(true);
        };

        img.onerror = () => {
            callback(false);
        };

        img.src = base64String;
    }
}
