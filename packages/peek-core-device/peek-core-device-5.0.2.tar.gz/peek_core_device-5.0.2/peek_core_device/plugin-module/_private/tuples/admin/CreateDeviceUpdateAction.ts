import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../../PluginNames";
import { DeviceUpdateTuple } from "../DeviceUpdateTuple";

@addTupleType
export class CreateDeviceUpdateAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "CreateDeviceUpdateAction";

    newUpdate: DeviceUpdateTuple;

    constructor() {
        super(CreateDeviceUpdateAction.tupleName);
    }
}
