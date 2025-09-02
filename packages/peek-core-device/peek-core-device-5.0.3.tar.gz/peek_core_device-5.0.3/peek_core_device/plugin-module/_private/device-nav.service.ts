
import { Injectable } from "@angular/core";
import { deviceBaseUrl } from "./PluginNames";

import { ActivatedRoute, Router, UrlSegment } from "@angular/router";

@Injectable()
export class DeviceNavService {
    homeUrl: UrlSegment[] = [];

    constructor(
        private route: ActivatedRoute,
        private router: Router,
    ) {
        // This is intended to route the web pages back to what ever URL
        // they have been routed from.
        this.route.url.subscribe(async (segments: UrlSegment[]) => {
            if (segments.length == 0) return;

            if (segments[0].path == deviceBaseUrl) return;

            if (segments[0].path == "") return;

            this.homeUrl = segments;
        });
    }

    async toHome(): Promise<boolean> {
        if (this.homeUrl.length != 0) 
            return await this.router.navigate(this.homeUrl);
        else 
            return await this.router.navigate([""]);
    }

    async toConnect(): Promise<boolean> {
        return await this.router.navigate([deviceBaseUrl, "connect"]);
    }

    async toConnecting(): Promise<boolean> {
        return await this.router.navigate([deviceBaseUrl, "connecting"]);
    }

    async toEnroll(): Promise<boolean> {
        return await this.router.navigate([deviceBaseUrl, "enroll"]);
    }

    async toEnrolling(): Promise<boolean> {
        return await this.router.navigate([deviceBaseUrl, "enrolling"]);
    }
}