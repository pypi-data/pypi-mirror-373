import { pluginAppRoutes } from "@_peek/plugin-app-routes";
import { pluginCfgRoutes } from "@_peek/plugin-cfg-routes";
import { DeviceEnrolledGuard } from "@peek/peek_core_device";
import { LoggedInGuard } from "@peek/peek_core_user";
import { ConfigPage, HomePage, UnknownRoutePage } from "./pages";
import { Route } from "@angular/router";

export const staticRoutes: Route[] = [
  {
    path: "peek_core_device",
    loadChildren: () =>
      import("@_peek/peek_core_device/device.module").then(
        (m) => m.DeviceModule,
      ),
  },
  {
    path: "peek_core_user",
    canActivate: [DeviceEnrolledGuard],
    loadChildren: () =>
      import("@_peek/peek_core_user/core-user-office.module").then(
        (m) => m.CoreUserOfficeModule,
      ),
  },
  // All routes require the device to be enrolled
  {
    path: "",
    canActivate: [DeviceEnrolledGuard, LoggedInGuard],
    children: [
      {
        path: "",
        component: HomePage,
      },
      ...pluginAppRoutes,
      ...pluginCfgRoutes,
    ],
  },
  {
    path: "config",
    component: ConfigPage,
  },
  {
    path: "**",
    component: UnknownRoutePage,
  },
];
