
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "core-device-loading",
    template: `
        <nz-spin nzTip="Loading...">
            <nz-empty nzNotFoundContent="Loading"></nz-empty>
        </nz-spin>
    `,
    styles: [`
        :host {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
        }
        
        nz-spin {
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
    `],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class LoadingComponent extends NgLifeCycleEvents {
    constructor() {
        super();
    }
}