import { CommonModule } from "@angular/common";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditBranchDetailComponent } from "./components/edit-branch-detail-table/edit.component";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import { BranchPageComponent } from "./components/branch-page/branch-page.component";

// Import Ant Design Modules
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzEmptyModule } from "ng-zorro-antd/empty";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";

export const pluginRoutes: Routes = [
    {
        path: "",
        component: BranchPageComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        ReactiveFormsModule,
        // Ant Design Modules
        NzTabsModule,
        NzTableModule,
        NzButtonModule,
        NzCardModule,
        NzInputModule,
        NzFormModule,
        NzGridModule,
        NzIconModule,
        NzEmptyModule,
        NzTagModule,
        NzDividerModule,
        NzInputNumberModule,
    ],
    declarations: [
        BranchPageComponent,
        EditBranchDetailComponent,
        EditSettingComponent,
    ],
})
export class BranchModule {}
