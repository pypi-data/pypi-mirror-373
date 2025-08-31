import { Component } from "@angular/core";
import { DeviceStatusService } from "@peek/peek_core_device";
import { UserService } from "@peek/peek_core_user";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, VortexStatusService } from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";

@Component({
  selector: "app-component",
  templateUrl: "app.component.html",
  styleUrls: ["app.component.scss"],
})
export class AppComponent extends NgLifeCycleEvents {
  loggedIn = false;

  constructor(
    private deviceStatusService: DeviceStatusService,
    public userService: UserService,
    private vortexStatusService: VortexStatusService,
    private balloonMsg: BalloonMsgService,
  ) {
    super();

    this.loggedIn = this.userService.loggedIn;
    this.userService.loggedInStatus
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((v) => (this.loggedIn = v));

    vortexStatusService.errors
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((msg: string) => balloonMsg.showError(msg));

    vortexStatusService.warning
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((msg: string) => balloonMsg.showWarning(msg));
  }

  showLoading(): boolean {
    return this.deviceStatusService.isLoading;
  }
}
