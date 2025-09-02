import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "@peek/peek_core_device/_private/PluginNames";
import { SERVER_INFO_TUPLE_DEFAULTS } from "./server-info-tuple-defaults";

@addTupleType
export class ServerInfoTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "ServerInfoTuple";

    host: string = SERVER_INFO_TUPLE_DEFAULTS.host;
    useSsl: boolean = SERVER_INFO_TUPLE_DEFAULTS.useSsl;
    httpPort: number = SERVER_INFO_TUPLE_DEFAULTS.httpPort;
    websocketPort: number = SERVER_INFO_TUPLE_DEFAULTS.websocketPort;
    hasConnected: boolean = SERVER_INFO_TUPLE_DEFAULTS.hasConnected;

    constructor() {
        super(ServerInfoTuple.tupleName);
    }
}
