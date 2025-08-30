import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class BandwidthTestTuple extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "DeviceBandwidthTestTuple";

    testData: boolean;

    constructor() {
        super(BandwidthTestTuple.tupleName);
    }
}
