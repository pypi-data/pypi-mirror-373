import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { SearchModule } from "@_peek/peek_core_search/search.module";
import { NzBadgeModule } from "ng-zorro-antd/badge";
import { HeaderComponent } from "./header";
import { StatusComponent } from "./status";
import { AngularSvgIconModule } from "angular-svg-icon";

const COMPONENTS = [HeaderComponent, StatusComponent];

@NgModule({
  declarations: COMPONENTS,
  imports: [
    RouterModule,
    FormsModule,
    BrowserModule,
    SearchModule,
    NzIconModule,
    NzBadgeModule,
    AngularSvgIconModule,
  ],
  exports: COMPONENTS,
})
export class ComponentsModule {}
