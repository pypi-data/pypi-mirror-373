import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";

// Import ng-zorro-antd modules
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzGridModule } from "ng-zorro-antd/grid";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzFormModule } from "ng-zorro-antd/form";

// Import our components
import { DiagramTracePageComponent } from "./components/diagram-trace-page/diagram-trace-page.component";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzCardModule } from "ng-zorro-antd/card";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: DiagramTracePageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzTabsModule,
        NzGridModule,
        NzTableModule,
        NzButtonModule,
        NzTagModule,
        NzDividerModule,
        NzInputModule,
        NzFormModule,
        NzInputNumberModule,
        NzCardModule,
    ],
    exports: [],
    providers: [],
    declarations: [DiagramTracePageComponent, EditSettingComponent],
})
export class DiagramTraceModule {}
