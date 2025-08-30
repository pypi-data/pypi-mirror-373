import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../../PluginNames";

// I'm using the word Alter here, because UpdateUpdate is confusing.
@addTupleType
export class AlterDeviceUpdateAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "AlterDeviceUpdateAction";

    updateId: number;
    isEnabled: boolean | null;
    remove: boolean = false;

    constructor() {
        super(AlterDeviceUpdateAction.tupleName);
    }
}
