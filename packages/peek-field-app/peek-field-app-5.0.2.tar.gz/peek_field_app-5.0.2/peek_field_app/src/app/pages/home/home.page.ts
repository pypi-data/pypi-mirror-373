import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService, IHeaderLink } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, VortexStatusService } from "@synerty/vortexjs";
import { homeLinks } from "@_peek/plugin-home-links";
import { BehaviorSubject, interval } from "rxjs";
import { takeUntil, throttle } from "rxjs/operators";
import { DeviceStatusService } from "@peek/peek_core_device";

@Component({
  selector: "home-page",
  templateUrl: "home.page.html",
  styleUrls: ["home.page.scss"],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomePage extends NgLifeCycleEvents {
  homeLinks = homeLinks;
  queuedActionCount$ = new BehaviorSubject<number>(0);
  isShowQueuedAction$ = new BehaviorSubject<boolean>(false);

  constructor(
    private headerService: HeaderService,
    private vortexStatusService: VortexStatusService,
    public deviceStatusService: DeviceStatusService,
  ) {
    super();
    headerService.setTitle("Peek Home");

    this.processQueuedActionCount(
      vortexStatusService.snapshot.queuedActionCount,
    );
    vortexStatusService.queuedActionCount
      .pipe(
        throttle(() => interval(2000), {
          leading: false,
          trailing: true,
        }),
        takeUntil(this.onDestroyEvent),
      )
      .subscribe((queuedActionCount: number) => {
        this.processQueuedActionCount(queuedActionCount);
      });
  }

  private processQueuedActionCount(queuedActionCount: number) {
    this.queuedActionCount$.next(queuedActionCount);
    if (queuedActionCount > 0) {
      this.isShowQueuedAction$.next(true);
    } else {
      this.isShowQueuedAction$.next(false);
    }
  }
}
