
import { Component, ChangeDetectionStrategy } from "@angular/core";
import {
    BalloonMsgLevel,
    BalloonMsgService,
    BalloonMsgType,
} from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleActionPushService,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import {
    AlterDeviceUpdateAction,
    DeviceUpdateTuple,
} from "@peek/peek_core_device/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "core-device-device-update",
    templateUrl: "./device-update.component.html",
    styleUrls: ["./device-update.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class DeviceUpdateComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<DeviceUpdateTuple[]>([]);

    constructor(
        private readonly balloonMsg: BalloonMsgService,
        private readonly actionService: TupleActionPushService,
        private readonly tupleDataObserver: TupleDataObserverService,
    ) {
        super();

        // Setup a subscription for the data
        this.tupleDataObserver
            .subscribeToTupleSelector(
                new TupleSelector(DeviceUpdateTuple.tupleName, {}),
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: DeviceUpdateTuple[]) => {
                this.items$.next(tuples);
            });
    }

    handleDeleteUpdate(item: DeviceUpdateTuple): void {
        const action = new AlterDeviceUpdateAction();
        action.updateId = item.id;
        action.remove = true;

        this.balloonMsg
            .showMessage(
                "Are you sure you'd like to delete this update?",
                BalloonMsgLevel.Warning,
                BalloonMsgType.ConfirmCancel,
                { confirmText: "Yes", cancelText: "No" },
            )
            .then(() => this.sendAction(action));
    }

    handleToggleUpdateEnabled(item: DeviceUpdateTuple): void {
        const action = new AlterDeviceUpdateAction();
        action.updateId = item.id;
        action.isEnabled = !item.isEnabled;

        const verb = item.isEnabled ? "DISABLE" : "enable";

        this.balloonMsg
            .showMessage(
                `Are you sure you'd like to ${verb} this update?`,
                BalloonMsgLevel.Warning,
                BalloonMsgType.ConfirmCancel,
                { confirmText: "Yes", cancelText: "No" },
            )
            .then(() => this.sendAction(action));
    }

    private sendAction(action: AlterDeviceUpdateAction): void {
        this.actionService
            .pushAction(action)
            .then(() => this.balloonMsg.showSuccess("Success"))
            .catch((e) => this.balloonMsg.showError(e));
    }
}