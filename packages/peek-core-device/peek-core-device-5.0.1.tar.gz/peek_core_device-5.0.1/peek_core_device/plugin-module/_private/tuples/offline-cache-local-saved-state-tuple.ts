import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class OfflineCacheLocalSavedStateTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheLocalStateTuple";

    lastCachingStartDate: Date | null = null;
    lastCachingCompleteDate: Date | null = null;

    constructor() {
        super(OfflineCacheLocalSavedStateTuple.tupleName);
    }
}
