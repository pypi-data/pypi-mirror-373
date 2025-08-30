import { Component, OnInit } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "core-device-loading",
    templateUrl: "loading.component.web.html",
})
export class LoadingComponent extends NgLifeCycleEvents implements OnInit {
    constructor(private headerService: HeaderService) {
        super();
    }

    override ngOnInit() {
        this.headerService.setEnabled(false);
        this.headerService.setTitle("");
    }
}
