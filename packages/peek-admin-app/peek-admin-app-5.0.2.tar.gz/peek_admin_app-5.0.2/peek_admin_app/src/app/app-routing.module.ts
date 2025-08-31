import { NgModule } from "@angular/core";
import { Route, RouterModule, Routes } from "@angular/router";
import { DashboardComponent } from "./components/dashboard/dashboard.component";
import { Tuple } from "@synerty/vortexjs";
import { pluginAppRoutes } from "@_peek/plugin-app-routes";
import { pluginCfgRoutes } from "@_peek/plugin-cfg-routes";

export const dashboardRoute: Route = {
    path: "",
    component: DashboardComponent,
};

const staticRoutes: Routes = [
    dashboardRoute,
    {
        path: "**",
        component: DashboardComponent,
    },
];

class PluginRoutesTuple extends Tuple {
    pluginName: string = "";
    lazyLoadModulePath: string = "";

    constructor() {
        super("peek_logic_service.PluginRoutesTuple");
    }
}

@NgModule({
    imports: [
        RouterModule.forRoot([
            ...pluginAppRoutes,
            ...pluginCfgRoutes,
            ...staticRoutes,
        ]),
    ],
    exports: [RouterModule],
})
export class AppRoutingModule {}
