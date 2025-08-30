import { addTupleType, TupleActionABC } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../../PluginNames";

@addTupleType
export class UpdateEnrollmentAction extends TupleActionABC {
    public static readonly tupleName =
        deviceTuplePrefix + "UpdateEnrollmentAction";

    deviceInfoId: number;
    unenroll: boolean = false;
    remove: boolean = false;

    constructor() {
        super(UpdateEnrollmentAction.tupleName);
    }
}
