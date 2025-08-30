import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { homeLinks } from "@_peek/plugin-home-links";
import {
  FooterService,
  HeaderService,
  IConfigLink,
  NavBackService,
} from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents } from "@synerty/vortexjs";
import { LoggedInGuard } from "@peek/peek_core_user";

@Component({
  selector: "sidebar-component",
  templateUrl: "sidebar.component.html",
  styleUrls: ["sidebar.component.scss"],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SidebarComponent extends NgLifeCycleEvents {
  homeLinks = homeLinks;
  configLinks: IConfigLink[] = [];

  showSearch$ = new BehaviorSubject<boolean>(false);
  title$ = new BehaviorSubject<string>("Peek");
  statusText$ = new BehaviorSubject<string>("");
  isEnabled$ = new BehaviorSubject<boolean>(true);

  constructor(
    private footerService: FooterService,
    public headerService: HeaderService,
    public navBackService: NavBackService,
    private loggedInGuard: LoggedInGuard,
  ) {
    super();

    this.headerService.title$
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((v) => (this.title = v));

    this.headerService.isEnabled$
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((v) => (this.isEnabled = v));

    this.footerService.statusText
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((v) => (this.statusText = v));

    this.configLinks = footerService.configLinksSnapshot;

    this.footerService.configLinks
      .pipe(takeUntil(this.onDestroyEvent))
      .subscribe((v) => (this.configLinks = v));
  }

  get showSearch() {
    return this.showSearch$.getValue();
  }

  set showSearch(value) {
    this.showSearch$.next(value);
  }

  get isEnabled() {
    return this.isEnabled$.getValue();
  }

  set isEnabled(value) {
    this.isEnabled$.next(value);
  }

  get statusText() {
    return this.statusText$.getValue();
  }

  set statusText(value) {
    this.statusText$.next(value);
  }

  get title() {
    return this.title$.getValue();
  }

  set title(value) {
    this.title$.next(value);
  }

  // ------------------------------
  // Display methods

  isBackButtonEnabled(): boolean {
    return this.navBackService.navBackLen() != 0;
  }

  showSearchClicked(): void {
    if (this.showSearch == true) {
      this.showSearch = false;
      return;
    }

    const canActivate: any = this.loggedInGuard.canActivate();
    if (canActivate === true) this.showSearch = true;
    else if (canActivate.then != null)
      canActivate.then((val: boolean) => (this.showSearch = val));
  }
}
