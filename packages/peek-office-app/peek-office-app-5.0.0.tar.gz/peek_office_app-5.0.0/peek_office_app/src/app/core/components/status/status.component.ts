import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, VortexStatusService } from "@synerty/vortexjs";
import { Network } from "@capacitor/network";

@Component({
  selector: "status-component",
  templateUrl: "status.component.html",
  styleUrls: ["status.component.scss"],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class StatusComponent extends NgLifeCycleEvents {
  isOnline$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(true);
  isVortexOnline$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(
    true,
  );

  constructor(
    public vortexStatusService: VortexStatusService,
    public headerService: HeaderService,
  ) {
    super();
    this.isVortexOnline = vortexStatusService.snapshot.isOnline;
  }

  get isOnline() {
    return this.isOnline$.getValue();
  }

  set isOnline(value) {
    this.isOnline$.next(value);
  }

  get isVortexOnline() {
    return this.isVortexOnline$.getValue();
  }

  set isVortexOnline(value) {
    this.isVortexOnline$.next(value);
  }

  override ngOnInit() {
    Network.addListener("networkStatusChange", (status) => {
      this.isOnline = status.connected;
    });
    this.vortexStatusService.isOnline
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((value) => (this.isVortexOnline = value));
  }
}
