import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { NzIconModule } from "ng-zorro-antd/icon";
import { HomePage, ConfigPage, UnknownRoutePage } from "./";
import { NzAlertModule } from "ng-zorro-antd/alert";

const PAGES = [HomePage, ConfigPage, UnknownRoutePage];

@NgModule({
  declarations: PAGES,
  imports: [
    RouterModule,
    FormsModule,
    BrowserModule,
    NzIconModule,
    NzAlertModule,
  ],
  exports: PAGES,
})
export class PagesModule {}
