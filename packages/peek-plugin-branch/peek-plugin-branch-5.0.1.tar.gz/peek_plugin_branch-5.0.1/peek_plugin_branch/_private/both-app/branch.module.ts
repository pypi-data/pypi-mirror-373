import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { BranchComponent } from "./branch.component";
import {
    branchFilt,
    branchObservableName,
    branchTupleOfflineServiceName,
} from "@peek/peek_plugin_branch/_private/PluginNames";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";
import { BranchDetailComponent } from "./branch-detail/branch-detail.component";
import { branchActionProcessorName } from "@peek/peek_plugin_branch/_private";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        branchActionProcessorName,
        branchFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(branchObservableName, branchFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(branchTupleOfflineServiceName);
}

// Define the child routes for this plugin.
export const pluginRoutes: Routes = [
    {
        path: "branchdetails",
        component: BranchDetailComponent,
    },
    {
        path: "",
        pathMatch: "full",
        component: BranchComponent,
    },
];

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routes and then select the component to load.
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzIconModule,
        HttpClientModule,
    ],
    exports: [],
    providers: [
        TupleActionPushOfflineService,
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
    declarations: [BranchComponent, BranchDetailComponent],
})
export class BranchModule {}
