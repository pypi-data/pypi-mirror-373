import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class DeviceBackgroundStateTupleAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "DeviceBackgroundStateTupleAction";

    deviceId: string;
    deviceBackgrounded: boolean;

    constructor() {
        super(DeviceBackgroundStateTupleAction.tupleName);
    }
}
