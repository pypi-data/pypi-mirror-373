import { Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";
import { DeviceStatusService, FontSizeService } from "@peek/peek_core_device";
import {
    BalloonMsgService,
    PageBodyService,
} from "@synerty/peek-plugin-base-js";
import { delay, takeUntil } from "rxjs/operators";
import { Subject } from "rxjs";

@Component({
    selector: "app-component",
    templateUrl: "app.component.html",
    styleUrls: ["app.component.scss"],
})
export class AppComponent extends NgLifeCycleEvents {
    fullScreen = false;
    scrollEnabled$ = new Subject<boolean>();

    constructor(
        public balloonMsg: BalloonMsgService,
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        private deviceStatusService: DeviceStatusService,
        private bodyService: PageBodyService,
        public fontSizeService: FontSizeService,
    ) {
        super();
        vortexStatusService.errors
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((msg: string) => {
                if ((msg || "").length === 0) {
                    console.log(
                        "An VortexStatusService" +
                            " error occured that had no text",
                    );
                } else {
                    balloonMsg.showError(msg);
                }
            });

        vortexStatusService.warning
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((msg: string) => {
                if ((msg || "").length === 0) {
                    console.log(
                        "An VortexStatusService" +
                            " warning occured that had no text",
                    );
                } else {
                    balloonMsg.showWarning(msg);
                }
            });
    }

    override ngOnInit() {
        this.bodyService.scrollEnabled$
            .pipe(delay(0), takeUntil(this.onDestroyEvent))
            .subscribe((value: boolean) => {
                this.scrollEnabled$.next(value);
            });
    }

    setBalloonFullScreen(enabled: boolean): void {
        this.fullScreen = enabled;
    }

    showLoading(): boolean {
        return this.deviceStatusService.isLoading;
    }
}
