import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class OfflineCacheStatusAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheStatusAction";

    deviceToken: string;
    encodedCombinedTuplePayload: string;
    lastCachingStartDate: Date | null;

    constructor() {
        super(OfflineCacheStatusAction.tupleName);
    }
}
