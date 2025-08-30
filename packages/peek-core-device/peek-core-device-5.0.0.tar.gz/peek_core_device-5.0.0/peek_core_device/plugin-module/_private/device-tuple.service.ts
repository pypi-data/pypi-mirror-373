import { Injectable } from "@angular/core";
import {
    TupleActionPushNameService,
    TupleActionPushOfflineService,
    TupleActionPushOfflineSingletonService,
    TupleActionPushService,
    TupleDataObservableNameService,
    TupleDataObserverService,
    TupleDataOfflineObserverService,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";

import {
    deviceActionProcessorName,
    deviceFilt,
    deviceObservableName,
    deviceTupleOfflineServiceName,
} from "./PluginNames";
import { HardwareInfo } from "./hardware-info/hardware-info";

/** Device Tuple Service
 *
 * This service provides the tuple action, observable and storage classes for the
 * other services in this plugin.
 *
 * Since there are sevaral services setting up their own instances of these, it made
 * sense to combine them all.
 *
 */
@Injectable()
export class DeviceTupleService {
    offlineStorage: TupleOfflineStorageService;
    offlineObserver: TupleDataOfflineObserverService;
    observer: TupleDataObserverService;

    tupleAction: TupleActionPushService;
    tupleOfflineAction: TupleActionPushOfflineService;

    hardwareInfo: HardwareInfo;

    constructor(
        storageFactory: TupleStorageFactoryService,
        actionSingletonService: TupleActionPushOfflineSingletonService,
        vortexService: VortexService,
        vortexStatusService: VortexStatusService,
    ) {
        // Create the offline storage
        this.offlineStorage = new TupleOfflineStorageService(
            storageFactory,
            new TupleOfflineStorageNameService(deviceTupleOfflineServiceName),
        );

        // Create the offline observer
        let observerName = new TupleDataObservableNameService(
            deviceObservableName,
            deviceFilt,
        );
        this.offlineObserver = new TupleDataOfflineObserverService(
            vortexService,
            vortexStatusService,
            observerName,
            this.offlineStorage,
        );

        // Create the observer
        this.observer = new TupleDataObserverService(
            this.offlineObserver,
            observerName,
        );

        // Create the observer
        this.tupleAction = new TupleActionPushService(
            new TupleActionPushNameService(
                deviceActionProcessorName,
                deviceFilt,
            ),
            vortexService,
            vortexStatusService,
        );

        // Create the observer
        this.tupleOfflineAction = new TupleActionPushOfflineService(
            new TupleActionPushNameService(
                deviceActionProcessorName,
                deviceFilt,
            ),
            vortexService,
            vortexStatusService,
            actionSingletonService,
        );

        this.hardwareInfo = new HardwareInfo(this.offlineStorage);
    }
}
