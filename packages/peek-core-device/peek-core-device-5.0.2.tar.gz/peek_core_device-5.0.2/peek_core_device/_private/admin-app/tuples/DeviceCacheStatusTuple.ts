import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "@peek/peek_core_device/_private";
import { OfflineCacheLoaderStatusTuple } from "@peek/peek_core_device/tuples/OfflineCacheLoaderStatusTuple";

@addTupleType
export class DeviceCacheStatusTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "DeviceCacheStatusTuple";

    statusList: OfflineCacheLoaderStatusTuple[] = [];

    constructor() {
        super(DeviceCacheStatusTuple.tupleName);
    }
}
