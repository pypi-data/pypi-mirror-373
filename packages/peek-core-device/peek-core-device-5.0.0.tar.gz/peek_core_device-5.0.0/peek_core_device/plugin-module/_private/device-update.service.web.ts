import { Injectable } from "@angular/core";
import { DeviceUpdateTuple } from "./tuples/DeviceUpdateTuple";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { DeviceServerService } from "./device-server.service";

@Injectable()
export class DeviceUpdateServiceDelegate {
    constructor(
        private serverService: DeviceServerService,
        private balloonMsg: BalloonMsgService,
    ) {}

    get updateInProgress(): boolean {
        return false;
    }

    updateTo(deviceUpdate: DeviceUpdateTuple): Promise<void> {
        return Promise.resolve();
    }
}
