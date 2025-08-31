import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditDocDbGenericMenuComponent } from "./components/edit-docdb-generic-menu-table/edit.component";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";

// Import our components
import { DocdbGenericMenuAdminPageComponent } from "./components/docdb-generic-menu-admin-page/docdb-generic-menu-admin-page.component";

// Import Ant Design Modules
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzAlertModule } from "ng-zorro-antd/alert";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: DocdbGenericMenuAdminPageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        ReactiveFormsModule,
        // Ant Design Modules
        NzTabsModule,
        NzButtonModule,
        NzTableModule,
        NzInputModule,
        NzFormModule,
        NzCardModule,
        NzIconModule,
        NzAlertModule,
        NzGridModule,
        NzSwitchModule,
        NzTagModule,
        NzDividerModule,
        NzInputNumberModule,
    ],
    exports: [],
    providers: [],
    declarations: [
        DocdbGenericMenuAdminPageComponent,
        EditDocDbGenericMenuComponent,
        EditSettingComponent,
    ],
})
export class DocDbGenericMenuModule {}
