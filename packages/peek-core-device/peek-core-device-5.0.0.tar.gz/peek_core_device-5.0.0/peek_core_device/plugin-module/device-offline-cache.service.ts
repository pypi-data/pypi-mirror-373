import { BehaviorSubject, Observable, Subject } from "rxjs";
import { Injectable } from "@angular/core";
import { filter, first, takeUntil } from "rxjs/operators";
import { Network } from "@capacitor/network";

import {
    NgLifeCycleEvents,
    Payload,
    TupleSelector,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { ClientSettingsTuple, DeviceTupleService } from "./_private";
import { OfflineCacheSettingTuple } from "./_private/tuples/OfflineCacheSettingTuple";
import { OfflineCacheLoaderStatusTuple } from "./tuples/OfflineCacheLoaderStatusTuple";
import { DeviceEnrolmentService } from "./device-enrolment.service";
import { DeviceInfoTuple } from "./DeviceInfoTuple";
import { DeviceBandwidthTestService } from "./_private/device-bandwidth-test.service";
import {
    OfflineCacheStatusTuple,
    StateMachineE,
} from "./_private/tuples/OfflineCacheStatusTuple";
import { OfflineCacheStatusAction } from "./_private/tuples/OfflineCacheStatusAction";
import { OfflineCacheCombinedStatusTuple } from "@peek/peek_core_device/_private/tuples/OfflineCacheCombinedStatusTuple";
import { OfflineCacheLocalSavedStateTuple } from "@peek/peek_core_device/_private/tuples/offline-cache-local-saved-state-tuple";

class Timer {
    private _startTime: Date;

    // Default to a year, it will never time out
    constructor(private timeoutSeconds: number = 365 * 24 * 60 * 68) {
        this._startTime = new Date();
    }

    get expired(): boolean {
        return (
            this._startTime.getTime() + this.timeoutSeconds * 1000 <
            new Date().getTime()
        );
    }

    get startTime(): Date {
        return this._startTime;
    }

    get expireTime(): Date {
        return new Date(this._startTime.getTime() + this.timeoutSeconds * 1000);
    }

    setTimeout(timeoutSeconds: number): void {
        this.timeoutSeconds = timeoutSeconds;
    }

    reset(startTime: null | Date = null): void {
        if (startTime != null) {
            this._startTime = startTime;
        } else {
            this._startTime = new Date();
        }
    }

    expire() {
        this._startTime = new Date(0);
    }
}

class RunLocker {
    private _locked: boolean = false;

    constructor() {}

    lock() {
        this._locked = true;
    }

    unlock() {
        this._locked = false;
    }

    get isLocked(): boolean {
        return this._locked;
    }
}

@Injectable()
export class DeviceOfflineCacheService extends NgLifeCycleEvents {
    private _offlineModeEnabled$ = new BehaviorSubject<boolean>(false);

    private _triggerCacheStart$ = new BehaviorSubject<boolean>(false);

    // This is not a behavior subject, because we want to be very controlled
    // about when we trigger pausing, we also don't need the BehaviorSubjects
    // emit on subscribe feature we never emit this during intialisation.
    private _isPaused = true;
    private _triggerCacheResume$ = new Subject<void>();

    private _loaderCachingStatus = {};
    private _loaderCachingStatus$ = new BehaviorSubject<
        OfflineCacheLoaderStatusTuple[]
    >([]);

    private readonly STATE_MACHINE_INTERVAL_SECONDS = 5.0;
    private readonly stateMachineLock = new RunLocker();

    private status: OfflineCacheStatusTuple | null = null;
    private _status$ = new BehaviorSubject<OfflineCacheStatusTuple>(
        new OfflineCacheStatusTuple(),
    );
    private settings: OfflineCacheSettingTuple | null = null;
    private allCientsSettingsTuple: ClientSettingsTuple | null = null;
    private deviceInfo: DeviceInfoTuple = new DeviceInfoTuple();

    private unsub = new Subject<void>();

    // Check the bandwidth every 5 minutes
    private readonly checkBandwidthTimer = new Timer();

    // Check the bandwidth every 15 minutes
    // This assumes the field device is transitioning through bad internet
    // If they turn on their wifi, we're in for a predicament.
    private readonly abortRetryTimer = new Timer();

    // Give loaders 60 seconds to pause
    private readonly pauseTimeoutTimer = new Timer();

    // This will be reinitialised when the settings come from the server
    private readonly scheduledNextCacheStartTimer = new Timer();

    // Run every 2 to 5 minutes, so we don't overload the server
    private readonly sendStateToServerTimer = new Timer();

    // Make note of the last network type
    private _lastNetworkType = "";

    private readonly savedStateTupleSelector = new TupleSelector(
        OfflineCacheLocalSavedStateTuple.tupleName,
        {},
    );

    private savedStateTuple: OfflineCacheLocalSavedStateTuple | null = null;

    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        private tupleService: DeviceTupleService,
        private enrolmentService: DeviceEnrolmentService,
        private deviceBandwidthTestService: DeviceBandwidthTestService,
    ) {
        super();

        // Restore our state
        this.loadStatusTuple();
        this.setupAllDevicesSettingsSubscription();

        // Why should we care if we're enrolled or not to check for updates?
        // Devices that are not enrolled should not be able to access anything on
        // the servers.
        this.enrolmentService
            .deviceInfoObservable()
            .subscribe((deviceInfo: DeviceInfoTuple) => {
                this.deviceInfo = deviceInfo;
                this.setupThisDeviceOfflineSettingsSubscription();
            });

        // Set the current network status
        Network.getStatus().then(
            (status) => (this._lastNetworkType = status.connectionType),
        );

        // If the user switches network types, then reset the abort timer
        Network.addListener("networkStatusChange", (status) => {
            if (!["wifi", "cellular"].includes(status.connectionType)) return;

            if (this._lastNetworkType !== status.connectionType) {
                this._lastNetworkType = status.connectionType;
                this.abortRetryTimer.expire();
            }
        });

        // Load the saved state
        this.loadSavedState();
    }

    private loadSavedState() {
        // Restore the next start date, if it exists
        // This subscription has to stay around, or the update will fail.
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(
                this.savedStateTupleSelector,
                false,
                false,
                true,
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: OfflineCacheLocalSavedStateTuple[] | null) => {
                // We need to keep the subscription, but only want to
                // process the update once
                if (this.savedStateTuple != null) {
                    return;
                }

                if ((tuples?.length || 0) === 0) {
                    this.savedStateTuple =
                        new OfflineCacheLocalSavedStateTuple();
                } else {
                    this.savedStateTuple = tuples[0];
                }

                this.status.lastCachingStartDate =
                    this.savedStateTuple.lastCachingStartDate;

                this.status.lastCachingCompleteDate =
                    this.savedStateTuple.lastCachingCompleteDate;

                console.log("Offline cache, loaded save state.");
                this.processStateLoaded();
            });
    }

    private saveSavedState() {
        this.savedStateTuple.lastCachingStartDate =
            this.status.lastCachingStartDate;

        this.savedStateTuple.lastCachingCompleteDate =
            this.status.lastCachingCompleteDate;

        this.tupleService.offlineObserver
            .updateOfflineState(this.savedStateTupleSelector, [
                this.savedStateTuple,
            ])
            .catch((e) =>
                console.error(
                    "ERROR, Failed to save" +
                        " OfflineCacheLocalSavedStateTuple",
                ),
            )
            .then(() => {
                console.log("Offline cache, saved save state.");
            });
    }

    private setupAllDevicesSettingsSubscription() {
        const ts = new TupleSelector(ClientSettingsTuple.tupleName, {});
        // noinspection TypeScriptValidateJSTypes
        this.tupleService.offlineObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((settings: ClientSettingsTuple[]) => {
                if (settings.length !== 0) {
                    this.allCientsSettingsTuple = settings[0];
                    this.setupTimersFromSettings();
                    this.processStateLoaded();
                }
            });
    }

    private setupTimersFromSettings(): void {
        this.sendStateToServerTimer.setTimeout(
            this.allCientsSettingsTuple.sendStateToServerSeconds +
                Math.floor(Math.random() * 5 * 60), // Add some randomness
        );
        this.scheduledNextCacheStartTimer.setTimeout(
            this.allCientsSettingsTuple.offlineCacheSyncSeconds,
        );
        this.checkBandwidthTimer.setTimeout(
            this.allCientsSettingsTuple.checkBandwidthSeconds,
        );
        this.pauseTimeoutTimer.setTimeout(
            this.allCientsSettingsTuple.pauseTimeoutSeconds,
        );
        this.abortRetryTimer.setTimeout(
            this.allCientsSettingsTuple.abortRetrySeconds,
        );
    }

    private setupThisDeviceOfflineSettingsSubscription() {
        this.unsub.next();

        const offlineSettingTs = new TupleSelector(
            OfflineCacheSettingTuple.tupleName,
            { deviceToken: this.deviceInfo.deviceToken },
        );

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(offlineSettingTs)
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(takeUntil(this.unsub))
            .pipe(filter((t) => t.length === 1))
            .subscribe((tuples: OfflineCacheSettingTuple[]) => {
                const oldSettings = this.settings;
                this.settings = tuples[0];
                this.processStateLoaded(oldSettings);
            });
    }

    private loadStatusTuple() {
        const offlineStateTs = new TupleSelector(
            OfflineCacheStatusTuple.tupleName,
            {},
        );

        this.tupleService.offlineObserver
            .subscribeToTupleSelector(offlineStateTs, false, false, true)
            .pipe(first())
            .subscribe((tuples: OfflineCacheStatusTuple[]) => {
                if (tuples.length === 1) {
                    this.status = tuples[0];
                } else {
                    this.status = new OfflineCacheStatusTuple();
                }
                this.processStateLoaded();
            });
    }

    private processStateLoaded(
        lastSettings: OfflineCacheSettingTuple | null = null,
    ) {
        if (
            this.savedStateTuple == null ||
            this.settings == null ||
            this.status == null ||
            this.allCientsSettingsTuple == null
        )
            return;

        console.assert(
            this.allCientsSettingsTuple.offlineCacheSyncSeconds >= 15 * 60,
            "Cache time is too small",
        );

        const calculatedEnabled =
            this.allCientsSettingsTuple.offlineMasterSwitchEnabled &&
            this.settings.offlineEnabled;

        // If there are no changes, then do nothing
        // Also, we get called everytime the Status tuple is stored.
        if (calculatedEnabled === lastSettings?.offlineEnabled) {
            return;
        }

        this._offlineModeEnabled$.next(calculatedEnabled);

        if (calculatedEnabled === true) {
            if (lastSettings?.offlineEnabled === false) {
                // This occurs when the peek admin has turned offline caching on
                // force a start now.
                this.status.state = StateMachineE.StartBandwidthTest;
            } else {
                // Caching is enabled
                // Update the cache timer and enable the offline caching
                this.status.state = StateMachineE.ScheduleNextRun;
            }
        } else {
            // Caching is disabled
            // If it's already disabled, do nothing
            if (this.status.state === StateMachineE.Disabled) {
                return;
            }

            this.status.state = StateMachineE.StartAborting;
            this.status.nextState = StateMachineE.Disabled;
        }
        // code change
        this.runStateMachine();
    }

    private sendStateToServer(force: boolean = false) {
        this._status$.next(this.status);

        if (!force && !this.sendStateToServerTimer.expired) return;
        if (!this.vortexStatusService.snapshot.isOnline) return;
        this.sendStateToServerTimer.reset();

        const combinedTuple = new OfflineCacheCombinedStatusTuple();
        combinedTuple.deviceToken = this.deviceInfo.deviceToken;
        combinedTuple.loaderStatusList = this._loaderCachingStatusList;
        combinedTuple.offlineCacheStatus = this.status;

        new Payload({}, [combinedTuple]) //
            .toEncodedPayload()
            .then((encodedPayload) => {
                const action = new OfflineCacheStatusAction();
                action.deviceToken = this.deviceInfo.deviceToken;
                action.encodedCombinedTuplePayload = encodedPayload;
                action.lastCachingStartDate = this.status.lastCachingStartDate;
                return this.tupleService.tupleAction.pushAction(action);
            })
            .then(() => console.log("Offline cache status sent successfully"))
            .catch((e) => console.log(`ERROR: ${e}`));
    }

    get isInRunStates(): boolean {
        return (
            this.status.state === StateMachineE.StartRunning ||
            this.status.state === StateMachineE.Running ||
            this.status.state === StateMachineE.StartPausing ||
            this.status.state === StateMachineE.Pausing
        );
    }

    private runStateMachine(): void {
        if (this.stateMachineLock.isLocked) return;

        this.stateMachineLock.lock();
        // console.log(`StateMachine Start = ${this.status.stateString}`);
        this.tryRunStateMachine() //
            .catch((e) => console.log(`ERROR asyncStateMachine: ${e}`))
            .then(() => {
                this.deviceBandwidthTestService.setOfflineCachingRunning(
                    this.isInRunStates,
                );
                // console.log(`StateMachine End = ${this.status.stateString}`);

                setTimeout(() => {
                    try {
                        // Don't unlock it until we're going to run next
                        this.stateMachineLock.unlock();
                        if (this.status.state === StateMachineE.Disabled)
                            return;
                        this.runStateMachine();
                    } catch (e) {
                        console.log(`ERROR runStateMachine timer: ${e}`);
                    }
                }, this.STATE_MACHINE_INTERVAL_SECONDS * 1000);
            });
    }

    private async tryRunStateMachine(): Promise<void> {
        this.status.nextStateCheckDate = null;
        // If a cache is in progress, then
        if (
            this.status.isCacheInProgress &&
            !this.vortexStatusService.snapshot.isOnline
        ) {
            this.status.state = StateMachineE.StartAborting;
            this.status.nextState = StateMachineE.AbortedDueToVortexOffline;
        }

        switch (this.status.state) {
            case StateMachineE.LoadingSettings: {
                // Do nothing, The state machine shouldn't be running
                return;
            }
            case StateMachineE.Disabled: {
                // Do nothing, The state machine shouldn't be running
                return;
            }
            case StateMachineE.ScheduleNextRun: {
                // Ensure the caching does not start before it's due to.
                if (this.status.lastCachingStartDate != null) {
                    this.scheduledNextCacheStartTimer.reset(
                        this.status.lastCachingStartDate,
                    );
                    this.saveSavedState();
                }
                this.status.state = StateMachineE.Enabled;
                break;
            }
            case StateMachineE.Enabled: {
                // If the cache was in progress, then restart it.
                // It must finish first, before we start
                // doing it to the schedule
                if (!this.status.hasCachingCompleted) {
                    this.status.state = StateMachineE.StartBandwidthTest;
                    break;
                }

                // Check if we should start the caching.
                if (this.scheduledNextCacheStartTimer.expired) {
                    this.status.state = StateMachineE.StartBandwidthTest;
                    break;
                }

                // Update status display
                this.status.nextStateCheckDate =
                    this.scheduledNextCacheStartTimer.expireTime;

                // Otherwise do nothing
                return;
            }
            case StateMachineE.StartRunning: {
                if (!this.isOfflineCachingRunning) {
                    // If caching is not running, start it
                    console.log(
                        "StateMachineE.StartRunning, Starting Offline Caching",
                    );
                    this.triggerCachingStart();
                } else if (this.isOfflineCachingPaused) {
                    // If it's paused then resume it
                    console.log(
                        "StateMachineE.StartRunning, Resuming Offline Caching",
                    );
                    this.triggerCachingResume();
                } else {
                    // If the caching should be running, and it's not paused
                    // then why are we here?
                    // Start it again
                    console.log(
                        "StateMachineE.StartRunning," +
                            " except we're already running",
                    );
                    this.triggerCachingStart();
                }

                this.status.setStarted();
                this.checkBandwidthTimer.reset();
                this.status.state = StateMachineE.Running;
                break;
            }
            case StateMachineE.Running: {
                // Check if the caching is finished, if so, mark it.
                if (this.areAllLoadersComplete()) {
                    this.status.state = StateMachineE.ScheduleNextRun;
                    this.status.setCompleted();
                    this.saveSavedState();
                    break;
                }

                // Are we due for a pause? If so, pause it and check
                if (this.checkBandwidthTimer.expired) {
                    this.status.state = StateMachineE.StartPausing;
                    this.status.nextState = StateMachineE.StartBandwidthTest;
                    break;
                }

                // Update status display
                this.status.nextStateCheckDate =
                    this.checkBandwidthTimer.expireTime;

                // Otherwise do nothing
                return;
            }
            case StateMachineE.StartPausing: {
                console.assert(this.status.nextState != null);

                if (
                    !this.isOfflineCachingPaused &&
                    this.isOfflineCachingRunning
                ) {
                    this.triggerCachingPause();
                } else {
                    console.log(
                        "StateMachineE.StartPausing," +
                            " except we're already paused",
                    );
                }

                this.status.state = StateMachineE.Pausing;
                this.pauseTimeoutTimer.reset();
                break;
            }
            case StateMachineE.Pausing: {
                console.assert(this.status.nextState != null);

                // Ensure we don't wait forever for things to pause.
                // Sometimes loaders don't receive a response
                //  from the server and stop
                if (!this.pauseTimeoutTimer.expired) {
                    // Update status display
                    this.status.nextStateCheckDate =
                        this.pauseTimeoutTimer.expireTime;

                    // While some loaders are running, do nothing
                    if (!this.areAllLoadersPaused()) {
                        return;
                    }
                }

                this.status.state = this.status.nextState;
                this.status.nextState = null;
                break;
            }
            case StateMachineE.StartBandwidthTest: {
                // If the test is already running, then wait until it's
                // finished to start one.
                if (this.deviceBandwidthTestService.isTestRunning) {
                    return;
                }

                // Trigger the start and move on.
                if (!this.deviceBandwidthTestService.startTest()) {
                    console.log("ERROR:Failed to start bandwidth test");
                }
                this.status.state = StateMachineE.PausedForBandwidthTest;
                break;
            }
            case StateMachineE.PausedForBandwidthTest: {
                // While the test is running, Do nothing
                // It has code to time its self out.
                if (this.deviceBandwidthTestService.isTestRunning) {
                    return;
                }

                // This is assigned for the admin interface to use
                this.status.isSlowNetwork =
                    this.deviceBandwidthTestService.isSlowNetwork;
                this.status.lastMetric =
                    this.deviceBandwidthTestService.lastMetric;

                // If the results are in, and the network is slow, then stop
                if (this.deviceBandwidthTestService.isSlowNetwork) {
                    this.status.state = StateMachineE.StartAborting;
                    this.status.nextState =
                        StateMachineE.AbortedDueToSlowNetwork;
                    break;
                }

                // Otherwise, continue on.
                this.status.state = StateMachineE.StartRunning;
                break;
            }
            case StateMachineE.StartAborting: {
                console.assert(this.status.nextState != null);
                this.triggerCachingStop();
                this.status.setAborted();
                this.status.state = this.status.nextState;
                this.status.nextState = null;
                this.abortRetryTimer.reset();
                break;
            }
            case StateMachineE.AbortedDueToSlowNetwork: {
                // Have we finished waiting for the abort retry timer
                // NOTE: See the constructor of this class, if the users switches
                // between WI-FI and Cellular, it will expire the abort timer
                if (this.abortRetryTimer.expired) {
                    // Resuming from a slow network stop is the same process
                    // as starting the caching from scratch
                    // It will first test the network again,
                    //  then end up back here if the network is too slow
                    this.status.state = StateMachineE.Enabled;
                    break;
                }

                // Update status display
                this.status.nextStateCheckDate =
                    this.abortRetryTimer.expireTime;

                // Otherwise, do nothing
                return;
            }
            case StateMachineE.AbortedDueToVortexOffline: {
                if (this.vortexStatusService.snapshot.isOnline) {
                    this.status.state = StateMachineE.Enabled;
                    break;
                }

                // Otherwise, do nothing
                return;
            }
            default: {
                throw new Error(
                    `State ${this.status.state} is not implemented`,
                );
            }
        }

        // Store our state.
        // Storing this every 5 seconds should be fine.
        await this.tupleService.offlineObserver.updateOfflineState(
            new TupleSelector(OfflineCacheStatusTuple.tupleName, {}),
            [this.status],
        );

        this.sendStateToServer();
    }

    private areAllLoadersPaused(): boolean {
        const list = this._loaderCachingStatusList;
        if (list.length === 0) {
            return false;
        }

        for (const loader of list) {
            if (!loader.paused) {
                return false;
            }
        }
        return true;
    }

    private areAllLoadersComplete(): boolean {
        const list = this._loaderCachingStatusList;
        if (list.length === 0) {
            return false;
        }

        for (const loader of list) {
            if (loader.loadingIncomplete) return false;
        }
        return true;
    }

    private triggerCachingStart(): void {
        this._isPaused = false;
        this._triggerCacheStart$.next(true);
    }

    private triggerCachingStop(): void {
        this._isPaused = true;
        this._triggerCacheStart$.next(false);
    }

    private triggerCachingPause(): void {
        // Don't emit the paused, the loaders will check this in their own time.
        this._isPaused = true;
    }

    private triggerCachingResume(): void {
        this._isPaused = false;
        this._triggerCacheResume$.next();
    }

    forceStart(): void {
        this.status.state = StateMachineE.StartRunning;
        this.status.nextState = null;
        this.triggerCachingStop();
    }

    get triggerCachingStartObservable(): Observable<boolean> {
        return this._triggerCacheStart$.asObservable();
    }

    get triggerCachingResumeObservable(): Observable<void> {
        return this._triggerCacheResume$;
    }

    get isOfflineCachingPaused(): boolean {
        return this._isPaused;
    }

    get isOfflineCachingRunning(): boolean {
        return this._triggerCacheStart$.getValue();
    }

    updateLoaderCachingStatus(status: OfflineCacheLoaderStatusTuple): void {
        this._loaderCachingStatus[status.key] = status;
        this._loaderCachingStatus$.next(this._loaderCachingStatusList);
    }

    private get _loaderCachingStatusList(): OfflineCacheLoaderStatusTuple[] {
        return Object.keys(this._loaderCachingStatus)
            .sort((one, two) => (one > two ? -1 : 1))
            .map((k) => this._loaderCachingStatus[k]);
    }

    get loaderStatus$(): BehaviorSubject<OfflineCacheLoaderStatusTuple[]> {
        return this._loaderCachingStatus$;
    }

    get status$(): BehaviorSubject<OfflineCacheStatusTuple | null> {
        return this._status$;
    }

    get offlineModeEnabled(): boolean {
        return this.settings?.offlineEnabled || false;
    }

    get offlineModeEnabled$(): Observable<boolean> {
        return this._offlineModeEnabled$;
    }

    get cachingEnabled(): boolean {
        return (
            this.settings?.offlineEnabled &&
            this.vortexStatusService.snapshot.isOnline
        );
    }
}
