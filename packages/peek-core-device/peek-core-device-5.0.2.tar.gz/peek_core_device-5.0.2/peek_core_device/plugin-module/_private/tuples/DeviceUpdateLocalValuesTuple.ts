import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";

/** Device Update - Local Values - Tuple
 *
 * This tuple is only present on the device, and it's used to store and retrieve
 * information needed for the update logic on this device to track the
 * update states.
 */
@addTupleType
export class DeviceUpdateLocalValuesTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "DeviceUpdateLocalValuesTuple";

    lastUpdateCheck: Date;
    updateVersion: string;
    appVersion: string;

    constructor() {
        super(DeviceUpdateLocalValuesTuple.tupleName);
    }
}
