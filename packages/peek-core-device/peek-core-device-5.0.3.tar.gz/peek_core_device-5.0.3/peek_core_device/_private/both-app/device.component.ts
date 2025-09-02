import { Component } from "@angular/core";
import { DeviceNavService } from "@peek/peek_core_device/_private";

@Component({
    selector: "core-device",
    templateUrl: "device.component.web.html",
})
export class DeviceComponent {
    constructor(public nav: DeviceNavService) {}
}
