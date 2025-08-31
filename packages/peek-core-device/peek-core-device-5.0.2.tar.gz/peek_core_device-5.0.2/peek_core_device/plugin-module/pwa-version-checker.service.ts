import { Injectable } from "@angular/core";
import { SwUpdate, VersionEvent } from "@angular/service-worker";
import { BehaviorSubject, throttleTime, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Injectable()
export class PwaVersionCheckerService {
    isNewVersionAvailable$ = new BehaviorSubject<boolean>(false);

    private readonly CHECK_INTERVAL_MILLISECONDS: number = 60 * 60 * 1000;
    private unsub = new Subject<void>();

    constructor(private swUpdate: SwUpdate) {
        if (!this.swUpdate.isEnabled) {
            return;
        }

        this.checkForUpdateOnce();
        this.setupCheckForUpdates();
    }

    private checkForUpdateOnce(): void {
        this.swUpdate.checkForUpdate().then((hasUpdate: boolean) => {
            if (hasUpdate) {
                this.isNewVersionAvailable$.next(true);
            }
        });
    }
    setupCheckForUpdates(): void {
        this.unsub.next();

        this.swUpdate.versionUpdates
            .pipe(takeUntil(this.unsub))
            .pipe(throttleTime(this.CHECK_INTERVAL_MILLISECONDS))
            .subscribe((evt: VersionEvent) => {
                switch (evt.type) {
                    case "VERSION_DETECTED":
                        console.log(
                            `Downloading new app version: ${evt.version.hash}`,
                        );
                        break;
                    case "VERSION_READY":
                        console.log(
                            `Current app version: ${evt.currentVersion.hash}`,
                        );
                        console.log(
                            `New app version ready for use: ${evt.latestVersion.hash}`,
                        );
                        this.isNewVersionAvailable$.next(true);
                        break;
                    case "VERSION_INSTALLATION_FAILED":
                        console.log(
                            `Failed to install app version '${evt.version.hash}': ${evt.error}`,
                        );
                        break;
                }
            });
    }

    applyUpdate(): void {
        // Reload the page to update to the latest version.
        document.location.reload();
    }
}
