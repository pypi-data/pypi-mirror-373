import { CommonModule } from "@angular/common";
import { NgModule } from "@angular/core";
import { LoadingComponent } from "@_peek/peek_core_device/loading/loading.component";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { HttpClientModule } from "@angular/common/http";

// Define the root module for this plugin.
// This module is loaded by the lazy loader, what ever this defines is what is started.
// When it first loads, it will look up the routes and then select the component to load.
@NgModule({
    imports: [CommonModule, FormsModule, NzIconModule, HttpClientModule],
    exports: [LoadingComponent],
    providers: [],
    declarations: [LoadingComponent],
})
export class DeviceLoadingModule {}
