import { Injectable } from "@angular/core";
import {
    ActivatedRouteSnapshot,
    CanActivate,
    RouterStateSnapshot,
} from "@angular/router";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { DeviceEnrolmentService } from "./device-enrolment.service";
import { DeviceNavService } from "./_private/device-nav.service";
import { DeviceServerService } from "./_private/device-server.service";
import { firstValueFrom } from "rxjs";

@Injectable()
export class DeviceEnrolledGuard implements CanActivate {
    constructor(
        private enrolmentService: DeviceEnrolmentService,
        private nav: DeviceNavService,
        private headerService: HeaderService,
        private serverService: DeviceServerService,
    ) {}

    async canActivate(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Promise<boolean> {
        // If the server service is still loading, come back later
        // This only applies to when the app is initialising
        if (this.serverService.isLoading) {
            await firstValueFrom(this.serverService.connInfoObserver);
            return this.canActivate(route, state);
        }

        if (!this.serverService.isSetup) {
            await this.nav.toConnect();
            return false;
        }

        // If the enrolment service is still loading, the come back later
        // This only applies to when the app is initialising
        if (this.enrolmentService.isLoading()) {
            await firstValueFrom(this.enrolmentService.deviceInfoObservable());
            return this.canActivate(route, state);
        }

        if (this.enrolmentService.isEnrolled()) {
            this.headerService.setEnabled(true);
            return true;
        }

        // This will take care of navigating to where to need to go to enroll
        if (this.enrolmentService.checkEnrolment()) {
            this.headerService.setEnabled(true);
            return true;
        }

        return false;
    }
}
