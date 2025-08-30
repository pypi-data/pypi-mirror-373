import { takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DeviceNavService,
    EnrolDeviceAction,
    HardwareInfo,
} from "@peek/peek_core_device/_private";
import { DeviceEnrolmentService } from "@peek/peek_core_device";

@Component({
    selector: "core-device-enrolling",
    templateUrl: "enrolling.component.web.html",
})
export class EnrollingComponent extends NgLifeCycleEvents implements OnInit {
    data: EnrolDeviceAction = new EnrolDeviceAction();
    private hardwareInfo: HardwareInfo;

    constructor(
        private balloonMsg: BalloonMsgService,
        private headerService: HeaderService,
        private nav: DeviceNavService,
        private enrolmentService: DeviceEnrolmentService,
    ) {
        super();

        // Make sure we're not on this page when things are fine.
        let sub = this.doCheckEvent
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => {
                if (this.enrolmentService.isEnrolled()) {
                    this.nav.toHome();
                    sub.unsubscribe();
                } else if (!this.enrolmentService.isSetup()) {
                    this.nav.toEnroll();
                    sub.unsubscribe();
                }
            });
    }

    override ngOnInit() {
        this.headerService.setEnabled(false);
        this.headerService.setTitle("");
    }
}
