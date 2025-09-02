import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class EnrolDeviceAction extends TupleActionABC {
    public static readonly tupleName = deviceTuplePrefix + "EnrolDeviceAction";

    description: string;
    deviceId: string;
    deviceType: string;
    appVersion: string;

    mdmDeviceName: string;
    mdmDeviceSerialNumber: string;
    mdmDeviceAssetId: string;
    mdmDeviceAllocatedTo: string;

    constructor() {
        super(EnrolDeviceAction.tupleName);
    }
}
