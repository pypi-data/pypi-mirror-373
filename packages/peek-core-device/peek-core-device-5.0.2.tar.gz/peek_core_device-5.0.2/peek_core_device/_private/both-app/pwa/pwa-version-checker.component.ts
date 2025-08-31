import { Component } from "@angular/core";
import { PwaVersionCheckerService } from "@peek/peek_core_device";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "pwa-app-version-checker-component",
    templateUrl: "./pwa-version-checker.component.html",
    styleUrls: ["./pwa-version-checker.component.scss"],
})
export class PwaVersionCheckerComponent {
    isVisible: boolean = true;
    constructor(public pwaVersionCheckerService: PwaVersionCheckerService) {}

    applyUpdate(): void {
        this.pwaVersionCheckerService.applyUpdate();
    }

    ignoreUpdate(): void {
        this.isVisible = false;
    }

    get hasUpdate$(): BehaviorSubject<boolean> {
        return this.pwaVersionCheckerService.isNewVersionAvailable$;
    }
}
