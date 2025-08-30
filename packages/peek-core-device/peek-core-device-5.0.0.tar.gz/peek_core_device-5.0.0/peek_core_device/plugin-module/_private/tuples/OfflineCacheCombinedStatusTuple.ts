import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";
import { OfflineCacheLoaderStatusTuple } from "../../tuples/OfflineCacheLoaderStatusTuple";
import { OfflineCacheStatusTuple } from "./OfflineCacheStatusTuple";

@addTupleType
export class OfflineCacheCombinedStatusTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheCombinedStatusTuple";

    deviceToken: string;
    loaderStatusList: OfflineCacheLoaderStatusTuple[] = [];
    offlineCacheStatus: OfflineCacheStatusTuple;

    constructor() {
        super(OfflineCacheCombinedStatusTuple.tupleName);
    }
}
