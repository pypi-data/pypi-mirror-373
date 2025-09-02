import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class UpdateAppliedAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "UpdateAppliedAction";

    deviceId: string;
    updateVersion: string | null;
    appVersion: string | null;
    error: string | null;

    constructor() {
        super(UpdateAppliedAction.tupleName);
    }
}
