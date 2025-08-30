import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { DeviceInfoTuple } from "./DeviceInfoTuple";
import { PrivateDeviceEnrolmentService } from "./_private/device-enrolment.service";
import { DeviceServerService } from "./_private/device-server.service";

@Injectable()
export class DeviceEnrolmentService {
    constructor(
        private serverService: DeviceServerService,

        private privateDeviceEnrolmentService: PrivateDeviceEnrolmentService,
    ) {}

    get deviceInfo(): DeviceInfoTuple {
        return this.privateDeviceEnrolmentService.deviceInfo;
    }

    get serverHttpUrl(): string {
        let host = this.serverService.serverHost;
        let httpProtocol = this.serverService.serverUseSsl ? "https" : "http";
        let httpPort = this.serverService.serverHttpPort;

        return `${httpProtocol}://${host}:${httpPort}`;
    }

    get serverWebsocketVortexUrl(): string {
        let host = this.serverService.serverHost;
        let wsProtocol = this.serverService.serverUseSsl ? "wss" : "ws";
        let wsPort = this.serverService.serverWebsocketPort;

        return `${wsProtocol}://${host}:${wsPort}/vortexws`;
    }

    checkEnrolment(): boolean {
        return this.privateDeviceEnrolmentService.checkEnrolment();
    }

    deviceInfoObservable(): Observable<DeviceInfoTuple> {
        return this.privateDeviceEnrolmentService.deviceInfoObservable();
    }

    isFieldService(): boolean {
        return this.privateDeviceEnrolmentService.isFieldService();
    }

    isOfficeService(): boolean {
        return this.privateDeviceEnrolmentService.isOfficeService();
    }

    isLoading(): boolean {
        return this.privateDeviceEnrolmentService.isLoading();
    }

    isSetup(): boolean {
        return this.privateDeviceEnrolmentService.isSetup();
    }

    isEnrolled(): boolean {
        return this.privateDeviceEnrolmentService.isEnrolled();
    }

    enrolmentToken(): string | null {
        return this.privateDeviceEnrolmentService.enrolmentToken();
    }
}
