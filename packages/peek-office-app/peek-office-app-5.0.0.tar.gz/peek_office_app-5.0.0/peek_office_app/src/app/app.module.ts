import { BrowserModule } from "@angular/platform-browser";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { NgModule, isDevMode } from "@angular/core";
import { FormsModule } from "@angular/forms";
import { RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import { BalloonMsgModule } from "@synerty/peek-plugin-base-js";
import {
  TupleActionPushOfflineSingletonService,
  TupleDataObservableNameService,
  TupleOfflineStorageNameService,
  TupleStorageFactoryService,
  TupleStorageFactoryServiceWeb,
  SqlFactoryService,
} from "@synerty/vortexjs";
import { staticRoutes } from "./app.routes";
import { peekRootServices } from "./app.services";
import { AppComponent } from "./core/components/app";
import { pluginRootModules } from "../@_peek/plugin-root-modules";
import { pluginRootServices } from "@_peek/plugin-root-services";
import { PluginRootComponent } from "./plugin-root.component";
import { en_US, NZ_I18N } from "ng-zorro-antd/i18n";
import { registerLocaleData } from "@angular/common";
import en from "@angular/common/locales/en";
import { SearchModule } from "@_peek/peek_core_search/search.module";
import { PagesModule } from "./pages/pages.module";
import { ComponentsModule } from "./core/components";
import { ServiceWorkerModule } from "@angular/service-worker";
import { environment } from "../environments/environment";

registerLocaleData(en);

export function tupleDataObservableNameServiceFactory() {
  return new TupleDataObservableNameService("peek_office_service", {
    plugin: "peek_office_service",
  });
}

export function tupleOfflineStorageNameServiceFactory() {
  return new TupleOfflineStorageNameService("peek_office_service");
}

@NgModule({
  declarations: [AppComponent, PluginRootComponent],
  bootstrap: [AppComponent],
  imports: [
    RouterModule.forRoot(staticRoutes),
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FormsModule,
    BalloonMsgModule,
    ...pluginRootModules,
    SearchModule,
    PagesModule,
    ComponentsModule,
    ServiceWorkerModule.register("ngsw-worker.js", {
      enabled: environment.serviceWorkerEnabled,
      // Register the ServiceWorker as soon as the application is stable
      // or after 30 seconds (whichever comes first).
      registrationStrategy: "registerImmediately",
    }),
  ],
  providers: [
    { provide: NZ_I18N, useValue: en_US },
    {
      provide: TupleStorageFactoryService,
      useClass: TupleStorageFactoryServiceWeb,
    },
    SqlFactoryService,
    TupleActionPushOfflineSingletonService,
    ...peekRootServices,
    ...pluginRootServices,
  ],
})
export class AppModule {}
