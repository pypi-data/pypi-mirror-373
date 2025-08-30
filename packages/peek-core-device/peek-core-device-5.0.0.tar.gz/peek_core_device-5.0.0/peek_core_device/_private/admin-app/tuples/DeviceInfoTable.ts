import { addTupleType, Tuple } from "@synerty/vortexjs";
import {
    DeviceTypeEnum,
    deviceTuplePrefix,
} from "@peek/peek_core_device/_private";
import {
    DeviceGpsLocationTuple,
    DeviceInfoTuple,
} from "@peek/peek_core_device";
import { Capacitor } from "@capacitor/core";

@addTupleType
export class DeviceInfoTable extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceInfoTable";

    static readonly TYPE_FIELD_IOS = DeviceInfoTuple.TYPE_FIELD_IOS;
    static readonly TYPE_FIELD_ANDROID = DeviceInfoTuple.TYPE_FIELD_ANDROID;
    static readonly TYPE_FIELD_WEB = DeviceInfoTuple.TYPE_FIELD_WEB;
    static readonly TYPE_OFFICE_WEB = DeviceInfoTuple.TYPE_OFFICE_WEB;
    static readonly TYPE_DESKTOP_WINDOWS = DeviceInfoTuple.TYPE_DESKTOP_WINDOWS;
    static readonly TYPE_DESKTOP_MACOS = DeviceInfoTuple.TYPE_DESKTOP_MACOS;

    static readonly DEVICE_OFFLINE = DeviceInfoTuple.DEVICE_OFFLINE;
    static readonly DEVICE_ONLINE = DeviceInfoTuple.DEVICE_ONLINE;
    static readonly DEVICE_BACKGROUND = DeviceInfoTuple.DEVICE_BACKGROUND;

    id: number;
    description: string;
    deviceId: string;
    deviceType: string;
    deviceToken: string;
    appVersion: string;
    updateVersion: string;
    lastOnline: Date;
    lastUpdateCheck: Date;
    createdDate: Date;
    deviceStatus: number;
    isEnrolled: boolean;
    isOfflineCacheEnabled: boolean;
    currentLocation: DeviceGpsLocationTuple;
    lastCacheUpdate: Date;
    lastBandwidthMetric: number;
    loggedInUser: string;
    lastCacheCheck: Date | null;
    lastDeviceIp: string;

    mdmDeviceName: string;
    mdmDeviceSerialNumber: string;
    mdmDeviceAssetId: string;
    mdmDeviceAllocatedTo: string;

    constructor() {
        super(DeviceInfoTable.tupleName);
    }

    get isWeb(): boolean {
        return !Capacitor.isNativePlatform();
    }

    get isBackgrounded(): boolean {
        return !!(this.deviceStatus & DeviceInfoTuple.DEVICE_BACKGROUND);
    }

    get googleMapLink() {
        if (!this.hasCurrentLocation()) {
            throw new Error("current location is not available");
        }
        return (
            "https://www.google.com/maps/search/?api=1&query=" +
            `${this.currentLocation.latitude},${this.currentLocation.longitude}`
        );
    }

    setDeviceType(val: DeviceTypeEnum) {
        switch (val) {
            case DeviceTypeEnum.DESKTOP_WEB:
                this.deviceType = DeviceInfoTuple.TYPE_OFFICE_WEB;
                break;

            case DeviceTypeEnum.DESKTOP_MACOS:
                this.deviceType = DeviceInfoTuple.TYPE_DESKTOP_MACOS;
                break;

            case DeviceTypeEnum.DESKTOP_WINDOWS:
                this.deviceType = DeviceInfoTuple.TYPE_DESKTOP_WINDOWS;
                break;

            case DeviceTypeEnum.FIELD_IOS:
                this.deviceType = DeviceInfoTuple.TYPE_FIELD_IOS;
                break;

            case DeviceTypeEnum.FIELD_ANDROID:
                this.deviceType = DeviceInfoTuple.TYPE_FIELD_ANDROID;
                break;

            case DeviceTypeEnum.MOBILE_WEB:
                this.deviceType = DeviceInfoTuple.TYPE_FIELD_WEB;
                break;
        }
    }

    hasCurrentLocation() {
        if (!this.currentLocation?.latitude) {
            return false;
        }
        if (typeof this.currentLocation.latitude === "number") {
            return true;
        }
        return false;
    }
}
