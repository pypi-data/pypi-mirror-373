import { DeviceGpsLocationTuple } from "./DeviceGpsLocationTuple";
import { Observable } from "rxjs";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

export abstract class DeviceGpsLocationService extends NgLifeCycleEvents {
    abstract location$: Observable<DeviceGpsLocationTuple | null>;
    abstract location: DeviceGpsLocationTuple | null;
}
