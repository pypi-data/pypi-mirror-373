import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { RouterModule } from "@angular/router";
import { FormsModule } from "@angular/forms";
import { SearchModule } from "@_peek/peek_core_search/search.module";
import { NzBadgeModule } from "ng-zorro-antd/badge";
import { NzAlertModule } from "ng-zorro-antd/alert";
import { NzIconModule } from "ng-zorro-antd/icon";
import { NzToolTipModule } from "ng-zorro-antd/tooltip";
import { NzButtonModule } from "ng-zorro-antd/button";
import { SidebarComponent } from "./sidebar";
import { StatusComponent } from "./status";

const COMPONENTS = [SidebarComponent, StatusComponent];

@NgModule({
  declarations: COMPONENTS,
  imports: [
    RouterModule,
    FormsModule,
    BrowserModule,
    SearchModule,
    NzIconModule,
    NzBadgeModule,
    NzAlertModule,
    NzToolTipModule,
    NzButtonModule,
  ],
  exports: COMPONENTS,
})
export class ComponentsModule {}
