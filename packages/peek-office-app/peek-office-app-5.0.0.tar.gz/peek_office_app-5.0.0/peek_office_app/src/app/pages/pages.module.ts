import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { NzAlertModule } from "ng-zorro-antd/alert";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzToolTipModule } from "ng-zorro-antd/tooltip";
import { NzButtonModule } from "ng-zorro-antd/button";
import { ConfigPage, HomePage, UnknownRoutePage } from "./";

const PAGES = [HomePage, ConfigPage, UnknownRoutePage];

@NgModule({
  declarations: PAGES,
  imports: [
    RouterModule,
    FormsModule,
    BrowserModule,
    NzAlertModule,
    NzIconModule,
    NzToolTipModule,
    NzButtonModule,
  ],
  exports: PAGES,
})
export class PagesModule {}
