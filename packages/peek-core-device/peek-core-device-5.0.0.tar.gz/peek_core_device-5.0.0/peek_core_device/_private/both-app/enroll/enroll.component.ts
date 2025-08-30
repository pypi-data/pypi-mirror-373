import { first, takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import {
    ClientSettingsTuple,
    DeviceNavService,
    DeviceTupleService,
    EnrolDeviceAction,
} from "@peek/peek_core_device/_private";
import {
    DeviceEnrolmentService,
    DeviceInfoTuple,
} from "@peek/peek_core_device";
import {
    DeviceTypeEnum,
    MdmAppConfigKeyEnum,
} from "@peek/peek_core_device/_private/hardware-info/hardware-info";

@Component({
    selector: "core-device-enroll",
    templateUrl: "enroll.component.web.html",
})
export class EnrollComponent extends NgLifeCycleEvents implements OnInit {
    data: EnrolDeviceAction = new EnrolDeviceAction();
    deviceType: DeviceTypeEnum;

    constructor(
        private balloonMsg: BalloonMsgService,
        private headerService: HeaderService,
        private tupleService: DeviceTupleService,
        private nav: DeviceNavService,
        private enrolmentService: DeviceEnrolmentService,
    ) {
        super();

        this.deviceType = this.tupleService.hardwareInfo.deviceType();

        // Make sure we're not on this page when things are fine.
        let sub = this.doCheckEvent
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => {
                if (this.enrolmentService.isEnrolled()) {
                    this.nav.toHome();
                    sub.unsubscribe();
                } else if (this.enrolmentService.isSetup()) {
                    this.nav.toEnrolling();
                    sub.unsubscribe();
                }
            });
    }

    override ngOnInit() {
        this.headerService.setEnabled(false);
        this.headerService.setTitle("");

        let t = this.deviceType;

        // Use DeviceInfoTuple to convert it.
        let deviceInfo = new DeviceInfoTuple();
        deviceInfo.setDeviceType(t);
        this.data.deviceType = deviceInfo.deviceType;

        this.tupleService.hardwareInfo.uuid().then((uuid) => {
            this.data.deviceId = uuid;

            this.maybeUpdateDeviceInfoFromMdm();

            this.checkForEnrollEnabled();
        });
    }

    enrollEnabled(): boolean {
        if (this.data.description == null || !this.data.description.length)
            return false;

        return true;
    }

    enrollClicked() {
        if (!this.enrollEnabled()) {
            this.balloonMsg.showWarning(
                "Please enter a unique description for this device",
            );
            return;
        }

        this.tupleService.tupleAction
            .pushAction(this.data)
            .then((tuples: DeviceInfoTuple[]) => {
                this.balloonMsg.showSuccess("Enrollment successful");
            })
            .catch((err) => {
                this.balloonMsg.showError(err);
            });
    }

    private checkForEnrollEnabled(): void {
        let ts = new TupleSelector(ClientSettingsTuple.tupleName, {});
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(first())
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((settings: ClientSettingsTuple[]) => {
                if (settings.length != 1) return;

                let setting: ClientSettingsTuple = settings[0];

                if (
                    this.tupleService.hardwareInfo.isOffice() &&
                    !setting.officeEnrollmentEnabled
                ) {
                    this.autoEnroll();
                } else if (
                    this.tupleService.hardwareInfo.isField() &&
                    !setting.fieldEnrollmentEnabled
                ) {
                    this.autoEnroll();
                }
            });
    }

    private autoEnroll(): void {
        this.data.description = this.data.deviceId;
        this.enrollClicked();
    }

    private maybeUpdateDeviceInfoFromMdm(): void {
        this.tupleService.hardwareInfo
            .queryMdmAppConfig(MdmAppConfigKeyEnum.DEVICE_NAME)
            .then((deviceName) => {
                if (deviceName != null) {
                    this.data.mdmDeviceName = deviceName;
                }
            });
        this.tupleService.hardwareInfo
            .queryMdmAppConfig(MdmAppConfigKeyEnum.DEVICE_SERIAL_NUMBER)
            .then((serialNumber) => {
                if (serialNumber != null) {
                    this.data.mdmDeviceSerialNumber = serialNumber;
                }
            });
        this.tupleService.hardwareInfo
            .queryMdmAppConfig(MdmAppConfigKeyEnum.DEVICE_ASSET_ID)
            .then((assetId) => {
                if (assetId != null) {
                    this.data.mdmDeviceAssetId = assetId;
                }
            });
        this.tupleService.hardwareInfo
            .queryMdmAppConfig(MdmAppConfigKeyEnum.DEVICE_ALLOCATED_TO)
            .then((allocatedTo) => {
                if (allocatedTo != null) {
                    this.data.mdmDeviceAllocatedTo = allocatedTo;
                }
            });
    }
}
