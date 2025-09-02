import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzDividerModule } from "ng-zorro-antd/divider";
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";

import {
    graphDbActionProcessorName,
    graphDbFilt,
    graphDbObservableName,
    graphDbTupleOfflineServiceName,
} from "@peek/peek_plugin_graphdb/_private";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import { StatusComponent } from "./components/status/status.component";
import { GraphdbAdminPageComponent } from "./components/graphdb-admin-page/graphdb-admin-page.component";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";
import { NzEmptyModule } from "ng-zorro-antd/empty";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        graphDbActionProcessorName,
        graphDbFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(
        graphDbObservableName,
        graphDbFilt,
    );
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(graphDbTupleOfflineServiceName);
}

export const pluginRoutes: Routes = [
    {
        path: "",
        component: GraphdbAdminPageComponent,
    },
];

@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzTabsModule,
        NzCardModule,
        NzTableModule,
        NzButtonModule,
        NzInputModule,
        NzTagModule,
        NzDividerModule,
        NzFormModule,
        NzInputNumberModule,
        NzDescriptionsModule,
        NzEmptyModule,
    ],
    exports: [],
    providers: [
        TupleActionPushService,
        {
            provide: TupleActionPushNameService,
            useFactory: tupleActionPushNameServiceFactory,
        },
        TupleOfflineStorageService,
        {
            provide: TupleOfflineStorageNameService,
            useFactory: tupleOfflineStorageNameServiceFactory,
        },
        TupleDataObserverService,
        TupleDataOfflineObserverService,
        {
            provide: TupleDataObservableNameService,
            useFactory: tupleDataObservableNameServiceFactory,
        },
    ],
    declarations: [
        GraphdbAdminPageComponent,
        EditSettingComponent,
        StatusComponent,
    ],
})
export class GraphDbModule {}
