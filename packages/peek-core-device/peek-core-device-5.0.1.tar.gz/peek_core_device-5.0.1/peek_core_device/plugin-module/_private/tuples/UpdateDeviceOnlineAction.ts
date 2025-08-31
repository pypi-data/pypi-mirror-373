import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";
import { DeviceInfoTuple } from "../../DeviceInfoTuple";

@addTupleType
export class UpdateDeviceOnlineAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "UpdateDeviceOnlineAction";

    DEVICE_OFFLINE = DeviceInfoTuple.DEVICE_OFFLINE;
    DEVICE_ONLINE = DeviceInfoTuple.DEVICE_ONLINE;
    DEVICE_BACKGROUND = DeviceInfoTuple.DEVICE_BACKGROUND;

    deviceId: string;
    deviceStatus: number;

    constructor() {
        super(UpdateDeviceOnlineAction.tupleName);
    }
}
