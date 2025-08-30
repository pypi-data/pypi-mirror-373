
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "device-admin",
    templateUrl: "device-page.component.html",
    styleUrls: ["./device-page.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DevicePageComponent extends NgLifeCycleEvents {
    constructor() {
        super();
    }
}