import { Component, ChangeDetectionStrategy } from "@angular/core";
import {
    BalloonMsgLevel,
    BalloonMsgService,
    BalloonMsgType,
} from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleActionABC,
    TupleActionPushService,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { DeviceInfoTable } from "../../tuples";
import { UpdateEnrollmentAction } from "@peek/peek_core_device/_private";
import { takeUntil } from "rxjs/operators";
import { DatePipe } from "@angular/common";
import { UpdateOfflineCacheSettingAction } from "../../tuples/UpdateOfflineCacheSettingAction";
import { BehaviorSubject } from "rxjs";

@Component({
    selector: "core-device-device-info",
    templateUrl: "./device-info.component.html",
    styleUrls: ["./device-info.component.scss"],
    providers: [DatePipe],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeviceInfoComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<DeviceInfoTable[]>([]);
    protected readonly deviceToken$ = new BehaviorSubject<string | null>(null);
    protected readonly isOfflineCacheModalShown$ = new BehaviorSubject<boolean>(
        false,
    );
    protected readonly deviceSearchVisible$ = new BehaviorSubject<boolean>(
        false,
    );
    protected readonly userSearchVisible$ = new BehaviorSubject<boolean>(false);
    protected readonly deviceSearchValue$ = new BehaviorSubject<string>("");
    protected readonly userSearchValue$ = new BehaviorSubject<string>("");

    private items: DeviceInfoTable[] = [];

    constructor(
        private readonly balloonMsg: BalloonMsgService,
        private readonly actionService: TupleActionPushService,
        private readonly tupleDataObserver: TupleDataObserverService,
        private readonly datePipe: DatePipe,
    ) {
        super();

        this.tupleDataObserver
            .subscribeToTupleSelector(
                new TupleSelector(DeviceInfoTable.tupleName, {}),
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                this.items = <DeviceInfoTable[]>tuples;
                this.refilter();
            });

        // Setup search value subscriptions
        this.deviceSearchValue$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.refilter());

        this.userSearchValue$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.refilter());
    }

    protected setDeviceSearchValue(value: string): void {
        this.deviceSearchValue$.next((value || "").toLowerCase());
    }

    protected setUserSearchValue(value: string): void {
        this.userSearchValue$.next((value || "").toLowerCase());
    }

    protected setOfflineCacheModalShown(value: boolean): void {
        this.isOfflineCacheModalShown$.next(value);
    }

    protected deviceStatus(device: DeviceInfoTable): string {
        if (
            device.deviceStatus & DeviceInfoTable.DEVICE_ONLINE &&
            !(device.deviceStatus & DeviceInfoTable.DEVICE_BACKGROUND)
        ) {
            return "Online, App Visible";
        }
        if (
            device.deviceStatus & DeviceInfoTable.DEVICE_ONLINE &&
            device.deviceStatus & DeviceInfoTable.DEVICE_BACKGROUND
        ) {
            return "Online, App Backgrounded";
        }
        if (device.lastOnline) {
            return (
                this.datePipe.transform(device.lastOnline, "medium") ||
                "Unknown"
            );
        }
        return "Never Connected";
    }

    protected hasDeviceInfoFromMdm(item: DeviceInfoTable): boolean {
        return !!(
            item.mdmDeviceName ||
            item.mdmDeviceSerialNumber ||
            item.mdmDeviceAssetId ||
            item.mdmDeviceAllocatedTo
        );
    }

    protected displayDeviceInfoFromMdm(item: DeviceInfoTable): string {
        return `Name: ${item.mdmDeviceName}, 
        Serial Number: ${item.mdmDeviceSerialNumber},
        Asset ID: ${item.mdmDeviceAssetId},
        Allocated To: ${item.mdmDeviceAllocatedTo}`;
    }

    protected handleDeleteDevice(item: DeviceInfoTable): void {
        const action = new UpdateEnrollmentAction();
        action.deviceInfoId = item.id;
        action.remove = true;

        this.balloonMsg
            .showMessage(
                "Are you sure you'd like to delete this device?",
                BalloonMsgLevel.Warning,
                BalloonMsgType.ConfirmCancel,
                { confirmText: "Yes", cancelText: "No" },
            )
            .then(() => this.sendAction(action));
    }

    protected handleToggleEnroll(item: DeviceInfoTable): void {
        const action = new UpdateEnrollmentAction();
        action.deviceInfoId = item.id;
        action.unenroll = item.isEnrolled;

        if (!action.unenroll) {
            this.sendAction(action);
            return;
        }

        this.balloonMsg
            .showMessage(
                "Are you sure you'd like to unenroll this device?",
                BalloonMsgLevel.Warning,
                BalloonMsgType.ConfirmCancel,
                { confirmText: "Yes", cancelText: "No" },
            )
            .then(() => this.sendAction(action));
    }

    protected handleToggleOfflineCacheEnabled(item: DeviceInfoTable): void {
        const newValue = !item.isOfflineCacheEnabled;
        const action = new UpdateOfflineCacheSettingAction();
        action.deviceInfoId = item.id;
        action.offlineCacheEnabled = newValue;

        this.sendAction(action).then(() => {
            item.isOfflineCacheEnabled = newValue;
        });
    }

    protected handleShowOfflineCacheStatus(item: DeviceInfoTable): void {
        this.deviceToken$.next(item.deviceToken);
        this.isOfflineCacheModalShown$.next(true);
    }

    private refilter(): void {
        const deviceSearchValue = this.deviceSearchValue$.getValue();
        const userSearchValue = this.userSearchValue$.getValue();

        const filter = (item: DeviceInfoTable) => {
            if (deviceSearchValue.length !== 0) {
                const val = (item.description || "").toLowerCase();
                if (val.indexOf(deviceSearchValue) === -1) return false;
            }
            if (userSearchValue.length !== 0) {
                const val = (item.loggedInUser || "").toLowerCase();
                if (val.indexOf(userSearchValue) === -1) return false;
            }
            return true;
        };

        const items = this.items.filter(filter);
        this.items$.next(items);
    }

    private sendAction(action: TupleActionABC): Promise<void> {
        return this.actionService
            .pushAction(action)
            .then(() => this.balloonMsg.showSuccess("Success"))
            .catch((e) => {
                this.balloonMsg.showError(e);
                throw e;
            });
    }
}
