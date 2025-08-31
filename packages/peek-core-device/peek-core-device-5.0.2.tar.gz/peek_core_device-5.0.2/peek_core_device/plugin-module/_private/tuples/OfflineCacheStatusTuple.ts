import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../PluginNames";
import { OfflineCacheLoaderStatusTuple } from "../../tuples/OfflineCacheLoaderStatusTuple";

export enum StateMachineE {
    LoadingSettings = 1,
    Disabled,
    ScheduleNextRun,
    Enabled,
    StartRunning,
    Running,
    StartPausing,
    Pausing,
    StartBandwidthTest,
    PausedForBandwidthTest,
    StartAborting,
    AbortedDueToSlowNetwork,
    AbortedDueToVortexOffline,
}

@addTupleType
export class OfflineCacheStatusTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheStatusTuple";

    // Checking occurs on start
    lastCachingCheckDate: Date | null;
    lastCachingStartDate: Date | null;
    lastCachingCompleteDate: Date | null;
    lastCachingAbortDate: Date | null;
    nextStateCheckDate: Date | null;

    state: StateMachineE = StateMachineE.LoadingSettings;
    nextState: StateMachineE | null = null;

    // Copied from the Testing service for data simplicity
    isSlowNetwork: boolean | null;
    lastMetric: number | null;

    constructor() {
        super(OfflineCacheLoaderStatusTuple.tupleName);
    }

    get isEnabled(): boolean {
        return !(
            this.state === StateMachineE.LoadingSettings ||
            this.state === StateMachineE.Disabled
        );
    }

    get stateString(): string {
        return StateMachineE[this.state];
    }

    get nextStateString(): string {
        return this.nextState == null ? "" : StateMachineE[this.nextState];
    }

    get secondsUntilNextStateCheckString(): string {
        if (this.nextStateCheckDate == null) return "";

        const diffSeconds =
            (this.nextStateCheckDate.getTime() - new Date().getTime()) / 1000;
        const hours = Math.floor(diffSeconds / 3600);
        const minutes = Math.floor(diffSeconds / 60) % 60;
        const seconds = Math.round(diffSeconds % 60);

        return `${hours}h, ${minutes}m, ${seconds}s`;
    }

    get isCacheInProgress(): boolean {
        return (
            this.lastCachingStartDate != null &&
            this.lastCachingCompleteDate == null &&
            this.lastCachingAbortDate == null
        );
    }

    get hasCachingCompleted(): boolean {
        return this.lastCachingCompleteDate != null;
    }

    get hasCacheEverStarted(): boolean {
        return this.lastCachingStartDate != null;
    }

    setChecked(): void {
        this.lastCachingCheckDate = new Date();
    }

    setStarted(): void {
        this.lastCachingCheckDate = new Date();
        this.lastCachingStartDate = this.lastCachingCheckDate;
        this.lastCachingAbortDate = null;
        this.lastCachingCompleteDate = null;
    }

    setCompleted(): void {
        this.lastCachingAbortDate = null;
        this.lastCachingCompleteDate = new Date();
    }

    setAborted(): void {
        // If the caching is complete, there is nothing to abort
        if (this.lastCachingCompleteDate != null) {
            return;
        }

        this.lastCachingAbortDate = new Date();
        this.lastCachingStartDate = null;
        this.lastCachingCompleteDate = null;
    }
}
