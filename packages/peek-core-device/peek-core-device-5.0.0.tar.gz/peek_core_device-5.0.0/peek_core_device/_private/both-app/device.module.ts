import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
// Import the default route component
import { DeviceComponent } from "./device.component";
// Import the required classes from VortexJS
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
// Import the names we need for the
import {
    deviceFilt,
    deviceObservableName,
    deviceTupleOfflineServiceName,
} from "@peek/peek_core_device/_private/PluginNames";
import { EnrollComponent } from "./enroll/enroll.component";
// Import the names we need for the
import { deviceActionProcessorName } from "@peek/peek_core_device/_private";
import { EnrollingComponent } from "./enrolling/enrolling.component";
import { ConnectComponent } from "./connect/connect.component";
import { ConnectingComponent } from "./connecting/connecting.component";
import { pluginRoutes } from "./device.routes";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";

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

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routs and then select the component to load.
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
    declarations: [
        DeviceComponent,
        EnrollComponent,
        EnrollingComponent,
        ConnectComponent,
        ConnectingComponent,
    ],
})
export class DeviceModule {}
