import { Component, Input, ChangeDetectionStrategy } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleActionPushService,
    TupleDataObserverService,
    TupleSelector,
} from "@synerty/vortexjs";
import { BehaviorSubject, Subject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { DatePipe } from "@angular/common";
import { OfflineCacheCombinedStatusTuple } from "@peek/peek_core_device/_private/tuples/OfflineCacheCombinedStatusTuple";

@Component({
    selector: "core-device-device-cache-status",
    templateUrl: "./device-cache-status.component.html",
    styleUrls: ["./device-cache-status.component.scss"],
    providers: [DatePipe],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DeviceCacheStatusComponent extends NgLifeCycleEvents {
    protected readonly combinedStatus$ =
        new BehaviorSubject<OfflineCacheCombinedStatusTuple | null>(null);

    @Input()
    deviceToken$: BehaviorSubject<string>;

    private unsub = new Subject<void>();
    constructor(
        private readonly balloonMsg: BalloonMsgService,
        private readonly actionService: TupleActionPushService,
        private readonly tupleDataObserver: TupleDataObserverService,
    ) {
        super();

        this.deviceToken$
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((deviceToken: string) => {
                this.unsub.next();
                if (!deviceToken) {
                    this.combinedStatus$.next(null);
                    return;
                }

                this.tupleDataObserver
                    .subscribeToTupleSelector(
                        new TupleSelector(
                            OfflineCacheCombinedStatusTuple.tupleName,
                            { deviceToken },
                        ),
                    )
                    .pipe(takeUntil(this.onDestroyEvent))
                    .pipe(takeUntil(this.unsub))
                    .subscribe((tuples: Tuple[]) => {
                        const statusTuples =
                            tuples as OfflineCacheCombinedStatusTuple[];
                        this.combinedStatus$.next(statusTuples[0] || null);
                    });
            });
    }
}
