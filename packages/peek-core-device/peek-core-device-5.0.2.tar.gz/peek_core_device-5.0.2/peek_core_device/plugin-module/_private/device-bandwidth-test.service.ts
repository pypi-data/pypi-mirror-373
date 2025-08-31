import { Injectable } from "@angular/core";
import { BehaviorSubject, Subject, interval } from "rxjs";
import { filter, first, takeUntil } from "rxjs/operators";
import { Network } from "@capacitor/network";

import {
    NgLifeCycleEvents,
    PayloadEndpoint,
    TupleSelector,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { deviceFilt } from "./PluginNames";
import { DeviceTupleService } from "./device-tuple.service";
import { BandwidthTestResultTuple } from "./tuples/BandwidthTestResultTuple";
import { ClientSettingsTuple } from "./tuples/ClientSettingsTuple";
import { DeviceEnrolmentService } from "../device-enrolment.service";

const deviceBandwidthTestFilt = Object.assign(
    { key: "deviceBandwidthTestFilt" },
    deviceFilt,
);

export interface BandwidthStatusI {
    isSlowNetwork: boolean | null;
    lastMetric: number | null;
}

@Injectable()
export class DeviceBandwidthTestService extends NgLifeCycleEvents {
    private bandwidthTestEndpoint: PayloadEndpoint;
    private unsubLastBandwidthTest = new Subject<void>();

    readonly RESPONSE_TIMEOUT_SECONDS = 30.0;
    private slowNetworkBandwidthMetricThreshold: number = 1200;
    private readonly CHECK_PERIOD_SECONDS = 15 * 60;
    private readonly CHECK_BACKOFF_SECONDS = 5;

    private _isSlowNetwork: boolean = true;
    private _lastMetric: number = 1300;

    private _testRunning: boolean = false;
    private _lastNetworkType: string | null = null;

    private _offlineCachingRunning: boolean = false;

    readonly status$ = new BehaviorSubject<BandwidthStatusI>({
        isSlowNetwork: null,
        lastMetric: null,
    });

    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        private tupleService: DeviceTupleService,
        private enrolmentService: DeviceEnrolmentService,
    ) {
        super();
        this.status$.next({
            isSlowNetwork: this._isSlowNetwork,
            lastMetric: this._lastMetric,
        });

        this.bandwidthTestEndpoint = vortexService.createEndpoint(
            this,
            deviceBandwidthTestFilt,
            false,
        );

        const ts = new TupleSelector(ClientSettingsTuple.tupleName, {});
        // noinspection TypeScriptValidateJSTypes
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((settings: ClientSettingsTuple[]) => {
                if (settings.length !== 0) {
                    this.slowNetworkBandwidthMetricThreshold =
                        settings[0].slowNetworkBandwidthMetricThreshold;
                }
            });

        interval(this.CHECK_PERIOD_SECONDS * 1000)
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(
                filter(
                    () =>
                        this.vortexStatusService.snapshot.isOnline &&
                        !this._testRunning &&
                        !this._offlineCachingRunning,
                ),
            )
            .subscribe(() => this.startTest());

        const startTestShortly = () => {
            setTimeout(() => this.startTest(), 30 * 1000);
        };

        // ?? seconds after coming online, start a test
        this.vortexStatusService.isOnline
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((online) => online))
            .subscribe(startTestShortly);

        // Set the current network status
        Network.getStatus().then(
            (status) => (this._lastNetworkType = status.connectionType),
        );

        Network.addListener("networkStatusChange", (status) => {
            if (!["wifi", "cellular"].includes(status.connectionType)) return;

            if (this._lastNetworkType !== status.connectionType) {
                this._lastNetworkType = status.connectionType;
                startTestShortly();
            }
        });

        // this service is constructed when the app starts,
        // check what our network is like, after all the subscriptions complete
        startTestShortly();
    }

    setOfflineCachingRunning(value: boolean): void {
        this._offlineCachingRunning = value;
    }

    get isSlowNetwork(): boolean {
        return this._isSlowNetwork;
    }

    get lastMetric(): number {
        return this._lastMetric;
    }

    get isTestRunning(): boolean {
        return this._testRunning;
    }

    startTest(): boolean {
        if (this._testRunning) {
            console.log("Subsequent call to start bandwidth test ignored");
            return false;
        }
        if (this._offlineCachingRunning) {
            console.log(
                "Offline cache test skipped while offline caching is" +
                    " in progres",
            );
            return false;
        }
        console.log("Starting bandwidth test");

        this._testRunning = true;

        this._performBandwidthTest()
            .catch((e) => console.log(`ERROR _performBandwidthTest: ${e}`))
            .then(() => {
                setTimeout(() => {
                    this._testRunning = false;
                }, this.CHECK_BACKOFF_SECONDS * 1000);
            });

        return true;
    }

    private _performBandwidthTest(): Promise<number | null> {
        if (this.enrolmentService.deviceInfo == null)
            throw new Error("We need a deviceInfo tuple set first");

        const startPoll = new Date().getTime();
        console.log(`Starting performance test`);

        return new Promise<number>((resolve, reject) => {
            const timeoutCallback = () => {
                this.unsubLastBandwidthTest.next();
                this.applyBandwidthMetric(null);
                console.log(
                    "Performance test response timed out after," +
                        ` ${this.RESPONSE_TIMEOUT_SECONDS}s`,
                );
                reject();
            };

            const responseTimeoutHandle = setTimeout(
                timeoutCallback,
                this.RESPONSE_TIMEOUT_SECONDS * 1000,
            );

            const receiveCallback = () => {
                clearTimeout(responseTimeoutHandle);

                const responseTimeMs = new Date().getTime() - startPoll;
                console.log(
                    `Performance test response received, took ${responseTimeMs}`,
                );
                this.applyBandwidthMetric(responseTimeMs);

                resolve(responseTimeMs);
            };

            // Add the callback to the endpoint, but just onece
            this.unsubLastBandwidthTest.next();
            this.bandwidthTestEndpoint.observable
                .pipe(
                    first(),
                    takeUntil(this.onDestroyEvent),
                    takeUntil(this.unsubLastBandwidthTest),
                )
                .subscribe(receiveCallback);

            // Finally request the response
            this.vortexService.sendFilt(deviceBandwidthTestFilt);
        });
    }

    private applyBandwidthMetric(responseTimeMs: number | null) {
        if (this._offlineCachingRunning) {
            return;
        }

        this._lastMetric = responseTimeMs;

        if (this.slowNetworkBandwidthMetricThreshold == null) {
            this._isSlowNetwork = true;
        } else if (responseTimeMs == null) {
            this._isSlowNetwork = true;
        } else {
            this._isSlowNetwork =
                this.slowNetworkBandwidthMetricThreshold < responseTimeMs;
        }
        this.status$.next({
            isSlowNetwork: this._isSlowNetwork,
            lastMetric: responseTimeMs,
        });
        this.sendBandwidthUpdate(responseTimeMs);
    }

    private sendBandwidthUpdate(responseTimeMs: number | null) {
        const action = new BandwidthTestResultTuple();
        action.metric = responseTimeMs;
        action.deviceToken = this.enrolmentService.deviceInfo.deviceToken;
        this.tupleService.tupleAction
            .pushAction(action)
            .catch((e) =>
                console.log(`Failed to send bandwidth update to server: ${e}`),
            );
    }
}
