import { addTupleType, Tuple } from "@synerty/vortexjs";
import { deviceTuplePrefix } from "../_private";

@addTupleType
export class OfflineCacheLoaderStatusTuple extends Tuple {
    public static readonly tupleName =
        deviceTuplePrefix + "OfflineCacheLoaderStatusTuple";

    pluginName: string;
    indexName: string;
    loadingQueueCount: number | null;
    totalLoadedCount: number | null;
    lastCheckDate: Date;
    initialFullLoadComplete: boolean;
    paused: boolean;

    constructor() {
        super(OfflineCacheLoaderStatusTuple.tupleName);
    }

    get key(): string {
        return `${this.pluginName}.${this.indexName}`;
    }

    get updateInProgress(): boolean {
        return (
            this.totalLoadedCount !== 0 &&
            this.loadingQueueCount < this.totalLoadedCount
        );
    }

    get loadingIncomplete(): boolean {
        return this.totalLoadedCount == null || this.loadingQueueCount !== 0;
    }

    get percentCompleteString(): string {
        return `${this.percentComplete}%`;
    }

    get percentComplete(): number {
        if (this.totalLoadedCount == null) {
            return 0;
        }
        if (this.totalLoadedCount === 0) {
            return 100;
        }
        const percent =
            (this.totalLoadedCount - this.loadingQueueCount) /
            this.totalLoadedCount;
        return Math.round(percent * 10000) / 100;
    }
}
