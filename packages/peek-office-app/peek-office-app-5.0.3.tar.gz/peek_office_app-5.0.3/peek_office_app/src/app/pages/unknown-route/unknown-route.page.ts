import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";

@Component({
  selector: "unknown-route-page",
  templateUrl: "unknown-route.page.html",
  styleUrls: ["unknown-route.page.scss"],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class UnknownRoutePage {
  constructor(public headerService: HeaderService) {
    headerService.setTitle("Unknown Route");
    this.headerService.isEnabled = true;
  }
}
