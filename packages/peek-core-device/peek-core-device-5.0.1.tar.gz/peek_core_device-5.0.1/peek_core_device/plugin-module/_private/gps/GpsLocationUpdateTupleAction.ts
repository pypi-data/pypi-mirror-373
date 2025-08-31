import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class GpsLocationUpdateTupleAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "GpsLocationUpdateTupleAction";
    public static readonly ACCURACY_COARSE = 1;
    public static readonly ACCURACY_FINE = 2;
    // This field allows customer specific data, that peek doesn't need to work
    data: { [key: string]: any } = {};

    latitude: number;
    longitude: number;
    updateType: number;
    datetime: Date;
    deviceToken: string;

    constructor() {
        super(GpsLocationUpdateTupleAction.tupleName);
    }
}
