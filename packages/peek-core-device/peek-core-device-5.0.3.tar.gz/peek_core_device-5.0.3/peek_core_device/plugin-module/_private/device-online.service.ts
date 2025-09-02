import { Injectable } from "@angular/core";
import { Subject } from "rxjs";
import { filter, first, takeUntil } from "rxjs/operators";

import { VortexService, VortexStatusService } from "@synerty/vortexjs";
import { DeviceTupleService } from "./device-tuple.service";
import { UpdateDeviceOnlineAction } from "./tuples/UpdateDeviceOnlineAction";

import { deviceFilt } from "./PluginNames";
import { PrivateDeviceEnrolmentService } from "./device-enrolment.service";

@Injectable()
export class DeviceOnlineService {
    private lastOnlineSub = new Subject<void>();
    private readonly deviceOnlineFilt = Object.assign(
        { key: "device.online" },
        deviceFilt,
    );
    constructor(
        private tupleService: DeviceTupleService,
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        private privateDeviceEnrolmentService: PrivateDeviceEnrolmentService,
    ) {}

    // @ts-ignore
    async setDeviceOnline(): Promise<void> {
        const data = new UpdateDeviceOnlineAction();

        data.deviceId = await this.tupleService.hardwareInfo.uuid();
        data.deviceStatus = data.DEVICE_ONLINE;

        this.tupleService.tupleAction
            .pushAction(data)
            .catch((error) => console.error(error));
    }

    async setDeviceOffline(): Promise<void> {
        const data = new UpdateDeviceOnlineAction();

        data.deviceId = await this.tupleService.hardwareInfo.uuid();
        data.deviceStatus = data.DEVICE_OFFLINE;

        this.tupleService.tupleAction
            .pushAction(data)
            .catch((error) => console.error(error));
    }

    /** Setup Online Ping
     *
     * This method sends a payload to the server when we detect that the vortex is
     * back online.
     *
     * The client listens for these payloads and tells the server acoordingly.
     *
     */
    setupOnlinePing() {
        this.lastOnlineSub.next();

        // Setup the online ping
        this.privateDeviceEnrolmentService
            .deviceInfoObservable()
            .pipe(first(), takeUntil(this.lastOnlineSub))
            .subscribe((deviceInfoTuple) => {
                let filt = Object.assign(
                    { deviceId: deviceInfoTuple.deviceId },
                    this.deviceOnlineFilt,
                );

                this.vortexStatusService.isOnline
                    .pipe(
                        filter((online) => online),
                        takeUntil(this.lastOnlineSub),
                    ) // Filter for online only
                    .subscribe(() => {
                        this.vortexService.sendFilt(filt);
                    });

                if (this.vortexStatusService.snapshot.isOnline)
                    this.vortexService.sendFilt(filt);
            });
    }
}
