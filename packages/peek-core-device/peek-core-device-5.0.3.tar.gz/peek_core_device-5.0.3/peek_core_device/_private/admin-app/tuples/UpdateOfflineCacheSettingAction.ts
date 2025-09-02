import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "@peek/peek_core_device/_private";

@addTupleType
export class UpdateOfflineCacheSettingAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "UpdateOfflineCacheSettingAction";
    deviceInfoId: number;
    offlineCacheEnabled: boolean;

    constructor() {
        super(UpdateOfflineCacheSettingAction.tupleName);
    }
}
