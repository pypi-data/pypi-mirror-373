import { Injectable } from "@angular/core";
import { DeviceServerService } from "./_private/device-server.service";
import { DeviceEnrolmentService } from "./device-enrolment.service";
import { Router } from "@angular/router";
import { deviceBaseUrl } from "./_private";
import { BehaviorSubject } from "rxjs";
import { DeviceBandwidthTestService } from "@peek/peek_core_device/_private/device-bandwidth-test.service";
import { takeUntil } from "rxjs/operators";

import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Injectable()
export class DeviceStatusService extends NgLifeCycleEvents {
    public readonly isNetworkSlow$ = new BehaviorSubject<boolean>(false);

    constructor(
        private router: Router,
        private enrolmentService: DeviceEnrolmentService,
        private deviceServerService: DeviceServerService,
        private deviceBandwidthTestService: DeviceBandwidthTestService,
    ) {
        super();
        deviceBandwidthTestService.status$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((status) =>
                this.isNetworkSlow$.next(status.isSlowNetwork),
            );
    }

    get isLoading(): boolean {
        // If we're currently showing a peek_core_device route then, loading = false
        let index = this.router.url.indexOf(deviceBaseUrl);
        if (0 <= index && index <= 4)
            // allow for "/..." etc
            return false;

        return (
            this.enrolmentService.isLoading() ||
            this.deviceServerService.isLoading
        );
    }
}
