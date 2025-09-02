import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class BandwidthTestResultTuple extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "BandwidthTestResultTuple";

    deviceToken: string;
    metric: number | null;

    get timedOut(): boolean {
        return this.metric == null;
    }

    constructor() {
        super(BandwidthTestResultTuple.tupleName);
    }
}
