import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { PwaVersionCheckerComponent } from "@_peek/peek_core_device/pwa/pwa-version-checker.component";
import { NzModalModule } from "ng-zorro-antd/modal";

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routes and then select the component to load.
@NgModule({
    imports: [CommonModule, NzModalModule],
    exports: [PwaVersionCheckerComponent],
    providers: [],
    declarations: [PwaVersionCheckerComponent],
})
export class PwaUpdatesModule {}
