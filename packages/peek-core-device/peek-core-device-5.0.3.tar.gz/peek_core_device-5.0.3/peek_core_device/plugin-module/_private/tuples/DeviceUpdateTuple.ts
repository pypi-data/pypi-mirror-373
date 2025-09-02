import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class DeviceUpdateTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceUpdateTuple";

    id: number;
    deviceType: string;
    description: string;
    buildDate: Date;
    appVersion: string;
    updateVersion: string;
    filePath: string;
    urlPath: string;
    fileSize: number;
    isEnabled: boolean;

    constructor() {
        super(DeviceUpdateTuple.tupleName);
    }
}
