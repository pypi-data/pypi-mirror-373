
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import {
    deviceFilt,
    SettingPropertyTuple,
} from "@peek/peek_core_device/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { NzMessageService } from "ng-zorro-antd/message";

@Component({
    selector: "core-device-edit-setting",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingPropertyTuple[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);

    private readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.SettingProperty",
    };

    constructor(
        private readonly balloonMsg: BalloonMsgService,
        private readonly vortexService: VortexService,
        private readonly message: NzMessageService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, deviceFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingPropertyTuple[]>tuples;
                this.items$.next(typedTuples);
                this.loading$.next(false);
            });
    }

    protected handleSave(): void {
        this.loading$.next(true);
        this.loader
            .save()
            .then(() => {
                this.message.success("Settings saved successfully");
            })
            .catch((e) => {
                this.message.error(`Failed to save settings: ${e}`);
            })
            .finally(() => {
                this.loading$.next(false);
            });
    }

    protected handleReset(): void {
        this.loading$.next(true);
        this.loader
            .load()
            .then(() => {
                this.message.success("Settings reset successfully");
            })
            .catch((e) => {
                this.message.error(`Failed to reset settings: ${e}`);
            })
            .finally(() => {
                this.loading$.next(false);
            });
    }
}