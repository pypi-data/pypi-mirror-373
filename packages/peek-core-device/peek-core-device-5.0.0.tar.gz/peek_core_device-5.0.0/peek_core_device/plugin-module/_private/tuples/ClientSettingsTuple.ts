import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

@addTupleType
export class ClientSettingsTuple extends Tuple {
    // The tuple name here should end in "Tuple" as well, but it doesn't, as it's a table
    public static readonly tupleName =
        deviceTuplePrefix + "ClientSettingsTuple";

    fieldEnrollmentEnabled: boolean;
    officeEnrollmentEnabled: boolean;
    slowNetworkBandwidthMetricThreshold: number;
    offlineMasterSwitchEnabled: boolean;

    offlineCacheSyncSeconds: number = 0;
    checkBandwidthSeconds: number = 0;
    abortRetrySeconds: number = 0;
    pauseTimeoutSeconds: number = 0;
    sendStateToServerSeconds: number = 0;

    constructor() {
        super(ClientSettingsTuple.tupleName);
    }
}
