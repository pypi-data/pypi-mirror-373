import { CommonModule } from "@angular/common";
import { HttpClientModule } from "@angular/common/http";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { DocdbComponent } from "./graphdb.component";
import { ViewTraceComponent } from "./view-trace/view.component";

// Define the child routes for this plugin.
export const pluginRoutes: Routes = [
    {
        path: "view_trace",
        component: ViewTraceComponent,
    },
    {
        path: "view_trace/:modelSetKey/:traceConfigKey/:startVertexKey",
        component: ViewTraceComponent,
    },
    {
        path: "",
        pathMatch: "full",
        component: DocdbComponent,
    },
];

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routes and then select the component to load.
@NgModule({
    imports: [
        CommonModule,
        HttpClientModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzIconModule,
    ],
    exports: [],
    providers: [],
    declarations: [DocdbComponent, ViewTraceComponent],
})
export class GraphDbModule {}
