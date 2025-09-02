import { Component, inject } from "@angular/core";
import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzSelectModule } from "ng-zorro-antd/select";
import { ConfigEditLookupLineStyleComponent } from "../config-editor-edit-lookup-line-style/config-edit-lookup-line-style.component";
import { NZ_MODAL_DATA } from "ng-zorro-antd/modal";

/**
 * Modal wrapper for ConfigEditLookupLineStyleComponent
 */
@Component({
    selector: "pl-config-editor-edit-lookup-line-style-modal",
    template: `
        <pl-diagram-config-edit-lookup-line-style
            [diagramConfigStateService]="data.diagramConfigStateService"
            [createMode]="data.createMode"
        >
        </pl-diagram-config-edit-lookup-line-style>
    `,
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
        NzSelectModule,
        ConfigEditLookupLineStyleComponent,
    ],
})
export class ConfigEditorEditLookupLineStyleModalComponent {
    data: any = inject(NZ_MODAL_DATA);
}
