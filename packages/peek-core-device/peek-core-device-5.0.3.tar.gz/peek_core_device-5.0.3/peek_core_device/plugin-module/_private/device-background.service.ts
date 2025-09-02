import { Injectable } from "@angular/core";
import { DeviceTupleService } from "./device-tuple.service";
import { App } from "@capacitor/app";
import { DeviceBackgroundStateTupleAction } from "./";

@Injectable()
export class DeviceBackgroundService {
    deviceId: string;
    deviceBackgrounded: boolean;

    constructor(private tupleService: DeviceTupleService) {
        this.tupleService.hardwareInfo
            .uuid()
            .then((uuid) => (this.deviceId = uuid));

        App.addListener("appStateChange", (state) => {
            this.deviceBackgrounded = !state.isActive;

            const action = new DeviceBackgroundStateTupleAction();
            action.deviceId = this.deviceId;
            action.deviceBackgrounded = this.deviceBackgrounded;

            this.tupleService.tupleAction
                .pushAction(action)
                .catch((e) =>
                    console.log(
                        `Failed to send device background update, Error: ${e}`,
                    ),
                );
        });
    }
}
