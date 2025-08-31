import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { HttpClientModule } from "@angular/common/http";
import { NzIconModule } from "ng-zorro-antd/icon";
import { CoreDeviceCfgComponent } from "./core-device-cfg.component";
import { ConnectComponent } from "./connect/connect.component";
import { NzButtonModule } from "ng-zorro-antd/button";
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
import {
    deviceFilt,
    deviceObservableName,
    deviceTupleOfflineServiceName,
} from "@peek/peek_core_device/_private/PluginNames";
import { deviceActionProcessorName } from "@peek/peek_core_device/_private";

export function tupleActionPushNameServiceFactory() {
    return new TupleActionPushNameService(
        deviceActionProcessorName,
        deviceFilt,
    );
}

export function tupleDataObservableNameServiceFactory() {
    return new TupleDataObservableNameService(deviceObservableName, deviceFilt);
}

export function tupleOfflineStorageNameServiceFactory() {
    return new TupleOfflineStorageNameService(deviceTupleOfflineServiceName);
}

// Define the child routes for this plugin.
export const pluginRoutes: Routes = [
    // {
    //     path: 'showDiagram',
    //     component: CoreDeviceCfgComponent
    // },
    {
        path: "",
        pathMatch: "full",
        component: CoreDeviceCfgComponent,
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
        NzButtonModule,
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
    declarations: [CoreDeviceCfgComponent, ConnectComponent],
})
export class CoreDeviceCfgModule {}
