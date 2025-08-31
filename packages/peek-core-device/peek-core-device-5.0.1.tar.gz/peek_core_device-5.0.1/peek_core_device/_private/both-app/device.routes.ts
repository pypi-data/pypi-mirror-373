import { Routes } from "@angular/router";
// Import the default route component
import { DeviceComponent } from "./device.component";
// Import the required classes from VortexJS
// Import the names we need for the
import { EnrollComponent } from "./enroll/enroll.component";
// Import the names we need for the
import { EnrollingComponent } from "./enrolling/enrolling.component";
import { ConnectComponent } from "./connect/connect.component";
import { ConnectingComponent } from "./connecting/connecting.component";

// Define the child routes for this plugin
export const pluginRoutes: Routes = [
    {
        path: "enrolling",
        component: EnrollingComponent,
    },
    {
        path: "enroll",
        component: EnrollComponent,
    },
    {
        path: "connect",
        component: ConnectComponent,
    },
    {
        path: "connecting",
        component: ConnectingComponent,
    },
    {
        path: "",
        pathMatch: "full",
        component: DeviceComponent,
    },
];
