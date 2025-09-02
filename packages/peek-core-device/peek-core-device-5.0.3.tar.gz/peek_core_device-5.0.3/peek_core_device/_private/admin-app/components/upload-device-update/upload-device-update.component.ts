
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Payload,
    PayloadEnvelope,
    VortexService,
} from "@synerty/vortexjs";
import {
    CreateDeviceUpdateAction,
    DeviceUpdateTuple,
} from "@peek/peek_core_device/_private";
import { BehaviorSubject } from "rxjs";
import { HttpClient, HttpEventType, HttpResponse } from "@angular/common/http";
import { NzUploadChangeParam, NzUploadFile, NzUploadXHRArgs } from "ng-zorro-antd/upload";
import { NzMessageService } from "ng-zorro-antd/message";

interface CustomUploadResponse {
    error?: string;
    message?: string;
}

@Component({
    selector: "core-device-upload-device-update",
    templateUrl: "./upload-device-update.component.html",
    styleUrls: ["./upload-device-update.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
})
export class UploadDeviceUpdateComponent extends NgLifeCycleEvents {
    protected readonly newUpdate = new DeviceUpdateTuple();
    protected readonly serverRestarting$ = new BehaviorSubject<boolean>(false);
    protected readonly progressPercentage$ = new BehaviorSubject<number | null>(null);
    protected readonly uploadEnabled$ = new BehaviorSubject<boolean>(false);
    protected readonly uploadUrl$ = new BehaviorSubject<string>("");
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    protected readonly deviceTypes = [
        { value: 'mobile-ios', label: 'Mobile - iOS' },
        { value: 'mobile-android', label: 'Mobile - Android' },
        { value: 'desktop-macos', label: 'Desktop - macOS' },
        { value: 'desktop-windows', label: 'Desktop - Windows' }
    ];

    private readonly filt = {
        plugin: "peek_logic_service",
        key: "peek_logic_service.plugin.version.info",
    };

    constructor(
        private readonly vortexService: VortexService,
        private readonly balloonMsg: BalloonMsgService,
        private readonly http: HttpClient,
        private readonly message: NzMessageService
    ) {
        super();
    }

    protected get isFormValid(): boolean {
        return !!(
            this.newUpdate.deviceType &&
            this.newUpdate.description &&
            this.newUpdate.appVersion &&
            this.newUpdate.updateVersion
        );
    }

    protected handleNext(): void {
        if (!this.isFormValid) {
            this.message.warning('Please fill in all required fields');
            return;
        }

        this.loading$.next(true);
        const action = new CreateDeviceUpdateAction();
        action.newUpdate = this.newUpdate;

        new Payload({}, [action])
            .makePayloadEnvelope()
            .then((payloadEnvelope: PayloadEnvelope) => payloadEnvelope.toVortexMsg())
            .then((vortexMsg: string) => {
                const data = encodeURIComponent(vortexMsg);
                const url = `/peek_core_device/create_device_update?payload=${data}`;
                this.uploadUrl$.next(url);
                this.uploadEnabled$.next(true);
            })
            .catch(err => {
                this.message.error(err);
            })
            .finally(() => {
                this.loading$.next(false);
            });
    }

    protected customUploadRequest = (item: NzUploadXHRArgs) => {
        const formData = new FormData();
        formData.append('file', item.file as any);
        
        return this.http.post(item.action!, formData, {
            reportProgress: true,
            observe: 'events'
        }).subscribe({
            next: (event: any) => {
                if (event.type === HttpEventType.UploadProgress) {
                    if (event.total! > 0) {
                        (event as any).percent = (event.loaded / event.total!) * 100;
                        this.progressPercentage$.next((event as any).percent);
                    }
                } else if (event instanceof HttpResponse) {
                    this.handleUploadResponse(event.body);
                }
            },
            error: err => {
                this.progressPercentage$.next(null);
                this.uploadEnabled$.next(false);
                this.message.error(`Upload failed: ${err.message}`);
                item.onError!(err, item.file);
            }
        });
    };

    protected handleUploadChange(info: NzUploadChangeParam): void {
        if (info.file.status === 'done') {
            this.handleUploadResponse(info.file.response);
        }
    }

    private handleUploadResponse(response: CustomUploadResponse): void {
        this.progressPercentage$.next(null);
        this.uploadEnabled$.next(false);

        if (response.error) {
            this.message.error(`Upload Failed: ${response.error}`);
        } else {
            this.serverRestarting$.next(true);
            this.message.success(`Upload Complete: ${response.message}`);
        }
    }
}