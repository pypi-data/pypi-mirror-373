import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class OfflineCacheSettingTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheSettingTuple";

    offlineEnabled: boolean = false;

    constructor() {
        super(OfflineCacheSettingTuple.tupleName);
    }
}
