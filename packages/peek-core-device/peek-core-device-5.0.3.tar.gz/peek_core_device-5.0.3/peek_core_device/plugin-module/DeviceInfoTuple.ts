import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "./_private/PluginNames";
import { DeviceTypeEnum } from "./_private/hardware-info/hardware-info";
import { DeviceGpsLocationTuple } from "./DeviceGpsLocationTuple";
import { Capacitor } from "@capacitor/core";

@addTupleType
export class DeviceInfoTuple extends Tuple {
    public static readonly tupleName = deviceTuplePrefix + "DeviceInfoTuple";

    static readonly TYPE_FIELD_IOS = "field-ios";
    static readonly TYPE_FIELD_ANDROID = "field-android";
    static readonly TYPE_FIELD_WEB = "field-web";
    static readonly TYPE_OFFICE_WEB = "office-web";
    static readonly TYPE_DESKTOP_WINDOWS = "desktop-windows";
    static readonly TYPE_DESKTOP_MACOS = "desktop-macos";

    static readonly DEVICE_OFFLINE = 0;
    static readonly DEVICE_ONLINE = 1;
    static readonly DEVICE_BACKGROUND = 2;

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
    currentLocation: DeviceGpsLocationTuple;

    lastDeviceIp: string;

    mdmDeviceName: string;
    mdmDeviceSerialNumber: string;
    mdmDeviceAssetId: string;
    mdmDeviceAllocatedTo: string;

    constructor() {
        super(DeviceInfoTuple.tupleName);
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
