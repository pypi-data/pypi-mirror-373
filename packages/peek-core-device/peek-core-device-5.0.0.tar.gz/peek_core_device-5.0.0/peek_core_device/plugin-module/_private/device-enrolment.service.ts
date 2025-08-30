import { Injectable } from "@angular/core";
import { BehaviorSubject, Observable } from "rxjs";
import { TupleSelector } from "@synerty/vortexjs";
import { filter } from "rxjs/operators";
import { DeviceInfoTuple } from "../DeviceInfoTuple";
import { DeviceNavService } from "./device-nav.service";
import { DeviceTupleService } from "./device-tuple.service";

@Injectable()
export class PrivateDeviceEnrolmentService {
    deviceInfo: DeviceInfoTuple = null;

    // There is no point having multiple services observing the same thing
    // So lets create a nice observable for the device info.
    private deviceInfoSubject = new BehaviorSubject<DeviceInfoTuple | null>(
        null,
    );

    private _isLoading = true;
    private isSetupGetter: any;

    constructor(
        private nav: DeviceNavService,
        private tupleService: DeviceTupleService,
    ) {
        this.tupleService.hardwareInfo.uuid().then((uuid) => {
            // Create the tuple selector
            let tupleSelector = new TupleSelector(DeviceInfoTuple.tupleName, {
                deviceId: uuid,
            });

            // This is an application permanent subscription
            this.tupleService.offlineObserver
                .subscribeToTupleSelector(tupleSelector)
                .subscribe((tuples: DeviceInfoTuple[]) => {
                    this._isLoading = false;

                    if (tuples.length == 1) {
                        this.deviceInfo = tuples[0];
                        this.deviceInfoSubject.next(this.deviceInfo);
                    } else {
                        this.deviceInfo = null;
                    }

                    this.checkEnrolment();
                });
        });
    }

    setServerIsSetupGetter(isSetupGetter: any) {
        // this is called from DeviceServerService
        this.isSetupGetter = isSetupGetter;
    }

    checkEnrolment(): boolean {
        if (!this.isSetupGetter()) return false;

        // Do Nothing
        if (this.deviceInfo == null) {
            console.log("Device Enrollment Has Not Started");
            this.nav.toEnroll();
            return false;
        }

        if (!this.deviceInfo.isEnrolled) {
            console.log("Device Enrollment Is Waiting Approval");
            this.nav.toEnrolling();
            return false;
        }

        return true;
    }

    deviceInfoObservable(): Observable<DeviceInfoTuple> {
        return this.deviceInfoSubject.pipe(
            filter((deviceInfo) => deviceInfo != null),
        );
    }

    isFieldService(): boolean {
        return this.tupleService.hardwareInfo.isField();
    }

    isOfficeService(): boolean {
        return this.tupleService.hardwareInfo.isOffice();
    }

    isLoading(): boolean {
        return this._isLoading;
    }

    isSetup(): boolean {
        return this.deviceInfo != null;
    }

    isEnrolled(): boolean {
        return this.deviceInfo != null && this.deviceInfo.isEnrolled;
    }

    enrolmentToken(): string | null {
        if (this.deviceInfo == null) return null;
        return this.deviceInfo.deviceToken;
    }
}
