import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Route, Routes } from "@angular/router";
import { EditSettingComponent } from "./components/edit-setting-table/edit.component";
import { NzTableModule } from "ng-zorro-antd/table";
import { NzSwitchModule } from "ng-zorro-antd/switch";
import { NzModalModule } from "ng-zorro-antd/modal";
import { NzToolTipModule } from "ng-zorro-antd/tooltip";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzEmptyModule } from "ng-zorro-antd/empty";
import { NzDropDownModule } from "ng-zorro-antd/dropdown";
// Import the required classes from VortexJS
import {
    TupleActionPushNameService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
} from "@synerty/vortexjs";
// Import our components
import { DevicePageComponent } from "./components/device-page/device-page.component";
import { DeviceInfoComponent } from "./components/device-info-table/device-info.component";
import {
    deviceActionProcessorName,
    deviceFilt,
    deviceObservableName,
    deviceTupleOfflineServiceName,
} from "@peek/peek_core_device/_private";
import { DeviceCacheStatusComponent } from "./components/device-cache-status/device-cache-status.component";
import { NzDescriptionsModule } from "ng-zorro-antd/descriptions";
import { NzTabsModule } from "ng-zorro-antd/tabs";
import { NzCardModule } from "ng-zorro-antd/card";
import { NzInputNumberModule } from "ng-zorro-antd/input-number";
import { NzFormModule } from "ng-zorro-antd/form";
import { NzInputModule } from "ng-zorro-antd/input";
import { NzButtonModule } from "ng-zorro-antd/button";
import { NzDividerModule } from "ng-zorro-antd/divider";
import { NzTagModule } from "ng-zorro-antd/tag";
import { NzProgressModule } from "ng-zorro-antd/progress";

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

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: DevicePageComponent,
    },
];

// Define the module
@NgModule({
    imports: [
        CommonModule,
        RouterModule.forChild(pluginRoutes),
        FormsModule,
        NzTableModule,
        NzSwitchModule,
        NzModalModule,
        NzToolTipModule,
        NzIconModule,
        NzEmptyModule,
        NzDropDownModule,
        NzDescriptionsModule,
        NzTabsModule,
        NzCardModule,
        NzInputNumberModule,
        NzFormModule,
        NzInputModule,
        NzButtonModule,
        NzDividerModule,
        NzTagModule,
        NzProgressModule,
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
        DevicePageComponent,
        DeviceInfoComponent,
        // DeviceUpdateComponent,
        // UploadDeviceUpdateComponent,
        EditSettingComponent,
        DeviceCacheStatusComponent,
    ],
})
export class DeviceModule {}
