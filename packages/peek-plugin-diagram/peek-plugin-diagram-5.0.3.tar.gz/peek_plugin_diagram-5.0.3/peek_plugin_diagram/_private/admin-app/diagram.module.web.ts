import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzBadgeModule } from "ng-zorro-antd/badge";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzTagModule } from "ng-zorro-antd/tag";

// Import our components
import { DiagramPageComponent } from "./components/diagram-page/diagram-page.component";
import { StatusComponent } from "./components/status/status.component";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";
import { ConfigEditorTabComponent } from "./components/config-editor-tab/config-editor-tab.component";
import { NzListModule } from "ng-zorro-antd/list";
import { ConfigEditorSelectorTreeComponent } from "./components/config-editor-selector-tree/config-editor-selector-tree.component";
import { NzTreeModule } from "ng-zorro-antd/tree";
import { ConfigEditorSelectorLookupListComponent } from "./components/config-editor-selector-lookup-list/config-editor-selector-lookup-list.component";
import { ConfigEditCanvasComponent } from "./components/config-editor-edit-canvas/config-edit-canvas.component";
import {
    AdminContentWrapperTupleDataLoaderComponent,
    AdminPanelHeaderForTupleLoaderDelegateComponent,
} from "@synerty/peek-plugin-base-js";
import { ConfigEditModelSetComponent } from "./components/config-editor-edit-model-set/config-edit-model-set.component";
import { ConfigEditLookupLevelComponent } from "./components/config-editor-edit-lookup-level/config-edit-lookup-level.component";
import { ConfigEditLookupLayerComponent } from "./components/config-editor-edit-lookup-layer/config-edit-lookup-layer.component";
import { ConfigEditLookupTextStyleComponent } from "./components/config-editor-edit-lookup-text-style/config-edit-lookup-text-style.component";
import { ConfigEditLookupLineStyleComponent } from "./components/config-editor-edit-lookup-line-style/config-edit-lookup-line-style.component";
import { NzEmptyModule } from "ng-zorro-antd/empty";
import { NzSelectModule } from "ng-zorro-antd/select";
import { ConfigEditLookupColorComponent } from "./components/config-editor-edit-lookup-color/config-edit-lookup-color.component";
import { ConfigEditorEditLookupColorModalComponent } from "./components/config-editor-edit-lookup-color-modal/config-editor-edit-lookup-color-modal.component";
import { ConfigEditorEditLookupLayerModalComponent } from "./components/config-editor-edit-lookup-layer-modal/config-editor-edit-lookup-layer-modal.component";
import { ConfigEditorEditLookupLevelModalComponent } from "./components/config-editor-edit-lookup-level-modal/config-editor-edit-lookup-level-modal.component";
import { ConfigEditorEditLookupLineStyleModalComponent } from "./components/config-editor-edit-lookup-line-style-modal/config-editor-edit-lookup-line-style-modal.component";
import { ConfigEditorEditLookupTextStyleModalComponent } from "./components/config-editor-edit-lookup-text-style-modal/config-editor-edit-lookup-text-style-modal.component";
import { NzToolTipModule } from "ng-zorro-antd/tooltip";
import { NzIconModule } from "ng-zorro-antd/icon";
import { DiagramLookupCreateEditSelectComponent } from "./components/diagram-lookup-create-edit-select/diagram-lookup-create-edit-select.component";
import { ConfigEditorSelectorLookupLayerTreeComponent } from "./components/config-editor-selector-lookup-layer-tree/config-editor-selector-lookup-layer-tree.component";
import { NzPopoverModule } from "ng-zorro-antd/popover";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: DiagramPageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        ReactiveFormsModule,
        NzTabsModule,
        NzTableModule,
        NzButtonModule,
        NzInputModule,
        NzCardModule,
        NzSwitchModule,
        NzFormModule,
        NzGridModule,
        NzBadgeModule,
        NzInputNumberModule,
        NzDividerModule,
        NzTagModule,
        NzDescriptionsModule,
        NzListModule,
        NzTreeModule,
        NzEmptyModule,
        NzSelectModule,
        NzIconModule,
        NzToolTipModule,
        NzPopoverModule,
        AdminPanelHeaderForTupleLoaderDelegateComponent,
        AdminContentWrapperTupleDataLoaderComponent,
        ConfigEditLookupColorComponent,
        ConfigEditLookupLayerComponent,
        ConfigEditLookupLevelComponent,
        ConfigEditLookupTextStyleComponent,
        ConfigEditLookupLineStyleComponent,
        ConfigEditorEditLookupColorModalComponent,
        ConfigEditorEditLookupLayerModalComponent,
        ConfigEditorEditLookupLevelModalComponent,
        ConfigEditorEditLookupLineStyleModalComponent,
        ConfigEditorEditLookupTextStyleModalComponent,
    ],
    exports: [],
    providers: [],
    declarations: [
        DiagramPageComponent,
        StatusComponent,
        EditSettingComponent,
        ConfigEditorTabComponent,
        ConfigEditorSelectorTreeComponent,
        ConfigEditorSelectorLookupListComponent,
        ConfigEditorSelectorLookupLayerTreeComponent,
        ConfigEditModelSetComponent,
        ConfigEditCanvasComponent,
        DiagramLookupCreateEditSelectComponent,
    ],
})
export class PeekPluginDiagramModule {}
