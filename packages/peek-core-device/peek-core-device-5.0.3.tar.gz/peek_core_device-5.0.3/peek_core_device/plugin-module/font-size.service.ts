import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";
import { TextZoom } from "@capacitor/text-zoom";
import { Capacitor } from "@capacitor/core";

@Injectable({
    providedIn: "root",
})
export class FontSizeService {
    readonly fontScale$ = new BehaviorSubject<number>(1);

    constructor() {
        if (Capacitor.isNativePlatform()) {
            setInterval(() => {
                this.initializeFontScaling() //
                    .catch((e) =>
                        console.log(`ERROR: getting font scaling: ${e}`),
                    );
            }, 5000);
        }
    }

    private async initializeFontScaling(): Promise<void> {
        // Get initial text zoom level
        const { value } = await TextZoom.getPreferred();
        const constrainedValue = Math.min(1.4, Math.max(1.0, value));
        if (constrainedValue !== this.fontScale) {
            this.fontScale$.next(constrainedValue);
        }
    }

    get fontScale(): number {
        return this.fontScale$.getValue();
    }
}
