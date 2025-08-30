import {
    addTupleType,
    Tuple,
    TupleOfflineStorageService,
    TupleSelector,
} from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";
import { isField as isFieldStatic } from "./is-field.mweb";
import { Capacitor } from "@capacitor/core";
import { Device } from "@capacitor/device";
import { AppConfig } from "@capacitor-community/mdm-appconfig";

export enum DeviceTypeEnum {
    MOBILE_WEB,
    FIELD_IOS,
    FIELD_ANDROID,
    DESKTOP_WEB,
    DESKTOP_WINDOWS,
    DESKTOP_MACOS,
}

export enum MdmAppConfigKeyEnum {
    // device
    DEVICE_NAME = "peek.device.name",
    DEVICE_SERIAL_NUMBER = "peek.device.serialNumber",
    DEVICE_ASSET_ID = "peek.device.assetId",
    DEVICE_ALLOCATED_TO = "peek.device.allocatedTo",

    // server info
    SERVER_CONNECTION_HAS_CONNECTED = "peek.serverConnection.hasConnected",
    SERVER_CONNECTION_HOST = "peek.serverConnection.host",
    SERVER_CONNECTION_USE_SSL = "peek.serverConnection.useSsl",
    SERVER_CONNECTION_HTTP_PORT = "peek.serverConnection.httpPort",
    SERVER_CONNECTION_WEBSOCKET_PORT = "peek.serverConnection.websocketPort",
}

export function isWeb(type: DeviceTypeEnum): boolean {
    return (
        type == DeviceTypeEnum.MOBILE_WEB || type == DeviceTypeEnum.DESKTOP_WEB
    );
}

export function isField(type: DeviceTypeEnum): boolean {
    return (
        type == DeviceTypeEnum.MOBILE_WEB ||
        type == DeviceTypeEnum.FIELD_IOS ||
        type == DeviceTypeEnum.FIELD_ANDROID
    );
}

export function isOffice(type: DeviceTypeEnum): boolean {
    return (
        type == DeviceTypeEnum.DESKTOP_MACOS ||
        type == DeviceTypeEnum.DESKTOP_WINDOWS ||
        type == DeviceTypeEnum.DESKTOP_WEB
    );
}

@addTupleType
class DeviceUuidTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceUuidTuple";

    uuid: string;

    constructor() {
        super(DeviceUuidTuple.tupleName);
    }
}

export class HardwareInfo {
    constructor(private tupleStorage: TupleOfflineStorageService) {}

    isWeb(): boolean {
        return isWeb(this.deviceType());
    }

    isField(): boolean {
        return isField(this.deviceType());
    }

    isOffice(): boolean {
        return isOffice(this.deviceType());
    }

    async uuid(): Promise<string> {
        return (await Device.getId()).identifier;
    }

    description(): string {
        return navigator.userAgent;
    }

    deviceType(): DeviceTypeEnum {
        // Field
        if (isFieldStatic) {
            switch (Capacitor.getPlatform()) {
                case "ios":
                    return DeviceTypeEnum.FIELD_IOS;
                case "android":
                    return DeviceTypeEnum.FIELD_ANDROID;
                case "web":
                default:
                    return DeviceTypeEnum.MOBILE_WEB;
            }
        }
        // Office
        else {
            return DeviceTypeEnum.DESKTOP_WEB;
        }
    }

    async queryMdmAppConfig(key: MdmAppConfigKeyEnum): Promise<string | null> {
        if (this.deviceType() != DeviceTypeEnum.FIELD_IOS) {
            return null;
        }
        const result = await AppConfig.getValue({
            key: key,
        });
        return result.value;
    }
}
