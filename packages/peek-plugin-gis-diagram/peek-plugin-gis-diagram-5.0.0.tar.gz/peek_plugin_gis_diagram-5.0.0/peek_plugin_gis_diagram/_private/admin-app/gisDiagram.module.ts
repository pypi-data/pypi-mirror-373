
import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzCardModule } from "ng-zorro-antd/card";
import { RouterModule, Routes } from "@angular/router";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
// Import our components
import { GisDiagramAdminPageComponent } from "./components/gis-diagram-page/gis-diagram-admin-page.component";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: GisDiagramAdminPageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzTabsModule,
        NzButtonModule,
        NzDividerModule,
        NzTagModule,
        NzCardModule
    ],
    exports: [],
    providers: [],
    declarations: [GisDiagramAdminPageComponent, EditSettingComponent],
})
export class GisDiagramModule {}