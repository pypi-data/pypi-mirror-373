import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService, NavBackService } from "@synerty/peek-plugin-base-js";
import { LoggedInGuard } from "@peek/peek_core_user";
import { BehaviorSubject, interval } from "rxjs";
import { VortexStatusService } from "@synerty/vortexjs";
import { throttle } from "rxjs/operators";
import { ThrottleConfig } from "rxjs";
import { DeviceStatusService } from "@peek/peek_core_device";

@Component({
  selector: "header-component",
  templateUrl: "header.component.html",
  styleUrls: ["header.component.scss"],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent {
  showSearch$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  queuedActionCount$ = new BehaviorSubject<number>(0);
  constructor(
    public headerService: HeaderService,
    private loggedInGuard: LoggedInGuard,
    public navBackService: NavBackService,
    private vortexStatusService: VortexStatusService,
    public deviceStatusService: DeviceStatusService,
  ) {
    vortexStatusService.queuedActionCount
      .pipe(
        throttle(() => interval(800), {
          leading: false,
          trailing: true,
        } as ThrottleConfig),
      )
      .subscribe((queuedActionCount: number) => {
        this.queuedActionCount$.next(queuedActionCount);
      });
  }

  get showSearch() {
    return this.showSearch$.getValue();
  }

  set showSearch(value) {
    this.showSearch$.next(value);
  }

  showSearchClicked(): void {
    if (this.showSearch) {
      this.showSearch = false;
    } else {
      const canActivate: any = this.loggedInGuard.canActivate();
      if (canActivate) {
        this.showSearch = true;
      } else if (canActivate.then) {
        canActivate.then((val: boolean) => (this.showSearch = val));
      }
    }
  }
}
