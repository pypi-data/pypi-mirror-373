import { takeUntil } from "rxjs/operators";
import { Component, OnInit } from "@angular/core";
import { BalloonMsgService, HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import {
    DeviceNavService,
    DeviceServerService,
    DeviceTupleService,
    ServerInfoTuple,
} from "@peek/peek_core_device/_private";
import {
    DeviceTypeEnum,
    MdmAppConfigKeyEnum,
} from "@peek/peek_core_device/_private/hardware-info/hardware-info";
import { Capacitor } from "@capacitor/core";
import { SERVER_INFO_TUPLE_DEFAULTS } from "@peek/peek_core_device/_private/tuples/server-info-tuple-defaults";

@Component({
    selector: "core-device-enroll",
    templateUrl: "connect.component.web.html",
})
export class ConnectComponent extends NgLifeCycleEvents implements OnInit {
    server: ServerInfoTuple = new ServerInfoTuple();
    httpPortStr: string = SERVER_INFO_TUPLE_DEFAULTS.httpPort.toString();
    websocketPortStr: string =
        SERVER_INFO_TUPLE_DEFAULTS.websocketPort.toString();
    deviceType: DeviceTypeEnum;
    isWeb: boolean;
    platform: string;

    constructor(
        private balloonMsg: BalloonMsgService,
        private headerService: HeaderService,
        private tupleService: DeviceTupleService,
        private nav: DeviceNavService,
        private deviceServerService: DeviceServerService,
    ) {
        super();
        this.platform = Capacitor.getPlatform();
        this.deviceType = this.tupleService.hardwareInfo.deviceType();
        this.isWeb = this.tupleService.hardwareInfo.isWeb();

        this.deviceServerService.connInfoObserver
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((info: ServerInfoTuple) => {
                this.server = info;
            });

        this.maybeUpdateServerInfoFromMdm();

        // Make sure we're not on this page when things are fine.
        let sub = this.doCheckEvent
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => {
                if (this.deviceServerService.isConnected) {
                    this.nav.toEnroll();
                    sub.unsubscribe();
                } else if (this.deviceServerService.isSetup) {
                    this.nav.toConnecting();
                    sub.unsubscribe();
                }
            });
    }

    override ngOnInit() {
        this.headerService.setEnabled(false);
        this.headerService.setTitle("");
    }

    connectEnabled(): boolean {
        if (this.server != null) {
            if (this.server.host == null || !this.server.host.length)
                return false;

            if (!parseInt(this.websocketPortStr)) return false;

            if (!parseInt(this.httpPortStr)) return false;
        }
        return true;
    }

    connectClicked() {
        try {
            this.server.httpPort = parseInt(this.httpPortStr);
            this.server.websocketPort = parseInt(this.websocketPortStr);
        } catch (e) {
            this.balloonMsg.showError("Port numbers must be integers.");
            return;
        }

        this.deviceServerService
            .setServer(this.server)
            .then(() => this.nav.toConnecting());
    }

    setUseSsl(val: boolean) {
        this.server.useSsl = val;
    }

    maybeUpdateServerInfoFromMdm(): void {
        this.tupleService.hardwareInfo
            .queryMdmAppConfig(MdmAppConfigKeyEnum.SERVER_CONNECTION_HOST)
            .then((host) => {
                if (host != null) {
                    this.server.host = host;
                }
            });

        this.tupleService.hardwareInfo
            .queryMdmAppConfig(MdmAppConfigKeyEnum.SERVER_CONNECTION_HTTP_PORT)
            .then((httpPort) => {
                if (httpPort != null) {
                    this.server.httpPort = parseInt(httpPort);
                }
            });

        this.tupleService.hardwareInfo
            .queryMdmAppConfig(
                MdmAppConfigKeyEnum.SERVER_CONNECTION_WEBSOCKET_PORT,
            )
            .then((websocketPort) => {
                if (websocketPort != null) {
                    this.server.websocketPort = parseInt(websocketPort);
                }
            });

        this.tupleService.hardwareInfo
            .queryMdmAppConfig(MdmAppConfigKeyEnum.SERVER_CONNECTION_USE_SSL)
            .then((useSsl) => {
                if (useSsl != null) {
                    const _useSsl = useSsl === "true";
                    this.server.useSsl = _useSsl;
                }
            });

        this.tupleService.hardwareInfo
            .queryMdmAppConfig(
                MdmAppConfigKeyEnum.SERVER_CONNECTION_HAS_CONNECTED,
            )
            .then((hasConnected) => {
                if (hasConnected != null) {
                    const _hasConnected = hasConnected === "true";
                    this.server.hasConnected = _hasConnected;
                }
            });
    }
}
