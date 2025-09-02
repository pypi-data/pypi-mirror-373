import { ChangeDetectionStrategy, Component } from "@angular/core";
import { HeaderService } from "@synerty/peek-plugin-base-js";
import { configLinks } from "@_peek/plugin-config-links";
import { environment } from "../../../environments/environment";
import { peekAppEnvironment } from "../../../environments/peek-app-environment";

@Component({
  selector: "config-page",
  templateUrl: "config.page.html",
  styleUrls: ["config.page.scss"],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfigPage {
  configLinks = configLinks;
  readonly appVersion: string = peekAppEnvironment.version;

  constructor(public headerService: HeaderService) {
    this.headerService.setTitle("Peek Config");
    this.headerService.isEnabled = true;
  }
}
